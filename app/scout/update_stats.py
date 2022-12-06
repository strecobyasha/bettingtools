"""
Get games statistics from the Api.

Make requests to the Api to get statistics for the latest games
with empty 'game_stats' field in the DB.
"""

from django.db.models import QuerySet

from scout.parsers import DetailsParser
from scout.updaters import GameDetailsUpdater
from scout.updates_managers import DetailsUpdatesManager


class StatsUpdater(GameDetailsUpdater):

    def update_details(self, games_to_update: QuerySet, games_stats: dict) -> None:
        # Prepare events data and update games in the DB.
        for game in games_to_update.iterator():
            stats = games_stats[game.api_game_id]
            home_team_id = game.home_team.api_team_id
            n = 1 if home_team_id == stats[1]['team']['id'] else 0
            game.home_team_stats = self.get_team_stats(stats[n]['statistics'])
            game.away_team_stats = self.get_team_stats(stats[1-n]['statistics'])

    def get_team_stats(self, data: list[dict]) -> dict:
        # Convert statistics data, received from the Api,
        # to the one-dimensional dictionary.
        team_stats = {}
        for item in data:
            team_stats[item['type']] = item['value']

        return team_stats


def updater() -> None:
    stats_updater = StatsUpdater(
        field_to_check='home_team_stats',
        fields_to_update=['home_team_stats', 'away_team_stats'],
        related='home_team',
    )
    stats_parser = DetailsParser(url_tail='fixtures/statistics')
    updates_manager = DetailsUpdatesManager(
        updater=stats_updater,
        parser=stats_parser,
    )
    updates_manager.start_updating()
