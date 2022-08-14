"""
Get games events from the Api.

Make requests to the Api to get events for the latest games
with empty 'game_events' field in the DB.
"""

from django.db.models import QuerySet

from scout.parsers import DetailsParser
from scout.updaters import GameDetailsUpdater
from scout.updates_managers import DetailsUpdatesManager


class EventsUpdater(GameDetailsUpdater):

    def update_details(self, games_to_update: QuerySet, games_events: dict) -> None:
        # Prepare events data and update games in the DB.
        for game in games_to_update:
            events = self.prepare_game_events(games_events[game.api_game_id])
            game.game_events = events

    def prepare_game_events(self, data: list[dict]) -> list:
        # Remove excessive data from the Api data,
        # such as logo link or team name.
        for item in data:
            item['team'] = item['team']['id']

        return data

def updater() -> None:
    events_updater = EventsUpdater(field_to_check='game_events', fields_to_update=['game_events'])
    events_parser = DetailsParser(url_tail='fixtures/events')
    updates_manager = DetailsUpdatesManager(
        updater=events_updater,
        parser=events_parser,
    )
    updates_manager.start_updating()
