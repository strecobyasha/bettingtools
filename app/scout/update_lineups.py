"""
Get games lineups from the Api.

Make requests to the Api to get lineups for the latest games
with empty 'lineups' field in the DB.
"""

from django.db.models import QuerySet

from scout.parsers import DetailsParser
from scout.updaters import GameDetailsUpdater
from scout.updates_managers import DetailsUpdatesManager


class LineupsUpdater(GameDetailsUpdater):

    def update_details(self, games_to_update: QuerySet, games_lineups: dict) -> None:
        # Prepare lineups and update games in the DB.
        for game in games_to_update:
            lineups = self.prepare_lineups(games_lineups[game.api_game_id])
            game.lineups = lineups

    def prepare_lineups(self, data: list[dict]) -> list:
        # Remove excessive data from the Api data,
        # such as logo link or coach photo.
        for item in data:
            item['team'].pop('name')
            item['team'].pop('logo')
            if 'photo' in item['coach']:
                item['coach'].pop('photo')

        return data


def updater() -> None:
    lineups_updater = LineupsUpdater(field_to_check='lineups', fields_to_update=['lineups'])
    lineups_parser = DetailsParser(url_tail='fixtures/lineups')
    updates_manager = DetailsUpdatesManager(
        updater=lineups_updater,
        parser=lineups_parser,
    )
    updates_manager.start_updating()
