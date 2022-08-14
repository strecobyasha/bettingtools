"""
Parsers for updating process.

"""

import asyncio
import os
import time
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Generator, Iterator, Union

import aiohttp
from aiohttp import ClientConnectorError
from django.db.models import QuerySet
from dotenv import load_dotenv

path = Path(__file__).resolve().parent.parent
load_dotenv(''.join([str(path), '/config/.env']))

# The range for which scores should be parsed.
SCORES_DELTA_BOTTOM = 7
SCORES_DELTA_TOP = 7

class Parser(ABC):

    def __init__(self, url_tail: str):
        self.url_tail = url_tail

    async def api_parser(self, querystring: dict) -> list:
        async with aiohttp.ClientSession() as session:
            url = f'https://api-football-v1.p.rapidapi.com/v3/{self.url_tail}'
            headers = {
                'x-rapidapi-key': os.environ.get('API_KEY'),
                'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
            }
            try:
                async with session.get(url, headers=headers, params=querystring, ssl=False) as response:
                    data = await response.json()
                    try:
                        return data['response']
                    except KeyError:
                        return []
            except ClientConnectorError:
                return []


    @abstractmethod
    def get_data(self, what_to_parse: Union[QuerySet, dict]) -> Union[dict, list, iter]:
        """ Initiate parsing data from API. """

    @abstractmethod
    def tasker(self, objects: Union[list, dict]) -> Union[dict, list, iter]:
        """ Call API parser. """


class DetailsParser(Parser):

    def split_games(self, games_to_parse: QuerySet, batch_size: int = 100) -> Generator:
        # Split games into batches.
        for i in range(0, len(games_to_parse), batch_size):
            yield games_to_parse[i:i + batch_size]

    def get_data(self, games_to_parse: QuerySet) -> dict:
        game_details = {}
        batched_games = self.split_games(games_to_parse)
        batch_counter = 0
        for batch in batched_games:
            batch_counter += 1
            if batch_counter > 3:
                # The API has limitations on the number of requests per minute.
                time.sleep(90)
                batch_counter = 0
            game_details.update(asyncio.run(self.tasker(batch)))

        return game_details

    async def tasker(self, batch: list) -> dict:
        batch_data = {}
        tasks = {}
        for api_game_id in batch:
            querystring = {'fixture': api_game_id}
            tasks[api_game_id] = asyncio.create_task(
                self.api_parser(querystring=querystring),
            )
        for game_id, task in tasks.items():
            response = await task
            if len(response) > 0:
                batch_data[game_id] = response

        return batch_data


class ScoresParser(Parser):

    def get_data(self, tours_to_parse: dict) -> list:
        # API data (last and future games).
        return asyncio.run(self.tasker(tours_to_parse))

    async def tasker(self, tours: dict) -> list:
        # Create a task for each tournament and make a request
        # to the Api to get latest and next games (date_from, date_to).
        tasks = []
        today = date.today()
        date_from = str((today - timedelta(days=SCORES_DELTA_BOTTOM)))
        date_to = str((today + timedelta(days=SCORES_DELTA_TOP)))
        for tour in tours.values():
            querystring = {
                'league': tour.api_tour_id,
                'season': tour.current_season,
                'from': date_from,
                'to': date_to,
            }
            tasks.append(
                asyncio.create_task(
                    self.api_parser(querystring=querystring),
                ),
            )
        games = []
        for task in tasks:
            response = await task
            if len(response) > 0:
                games.extend(response)

        return games


class StandingsParser(Parser):

    def get_data(self, tours_to_parse: dict) -> iter:
        return asyncio.run(self.tasker(tours_to_parse))

    async def tasker(self, tours: dict) -> Iterator[Any]:
        tasks = []
        for tour in tours.values():
            querystring = {
                'league': tour.api_tour_id,
                'season': tour.current_season,
            }
            tasks.append(
                asyncio.create_task(
                    self.api_parser(querystring=querystring),
                ),
            )
        standings = []
        for task in tasks:
            response = await task
            if len(response) > 0 and 'league' in response[0]:
                standings.append(response[0]['league'])

        return iter(standings)
