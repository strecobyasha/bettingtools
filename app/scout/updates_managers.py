"""
Updates managers.

Define the order of the updating process.

"""

from abc import ABC, abstractmethod


class UpdatesManager(ABC):

    def __init__(self, updater, parser):
        self.updater = updater
        self.parser = parser

    @abstractmethod
    def start_updating(self) -> None:
        """ Start data parsing and DB updating """


class DetailsUpdatesManager(UpdatesManager):

    def start_updating(self) -> None:
        games_to_parse = self.updater.get_games_from_db()
        games_details = self.parser.get_data(games_to_parse)
        games_to_update = self.updater.get_games_to_update(games_details)
        self.updater.update_details(games_to_update, games_details)
        self.updater.update_games(games_to_update)


class ScoresUpdatesManager(UpdatesManager):

    def start_updating(self) -> None:
        tours_to_parse = self.updater.get_running_tours()
        games = self.parser.get_data(tours_to_parse)
        data_to_load = self.updater.prepare_data(games, tours_to_parse)
        self.updater.update_or_create_games(data_to_load)


class StandingsUpdatesManager(UpdatesManager):

    def start_updating(self) -> None:
        tours_to_parse = self.updater.get_running_tours()
        standings_data = self.parser.get_data(tours_to_parse)
        tours_to_update = self.updater.prepare_data(standings_data, tours_to_parse)
        self.updater.update_tours(tours_to_update)
