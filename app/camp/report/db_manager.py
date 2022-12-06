"""
Read and write games.

Collect games from the database to update report.

"""

from datetime import datetime, timedelta

from django.db.models import Q, QuerySet

from arena.models import Game
from camp.models import TeamModel
from camp.report_text_generator.text_manager import Report


class DataBaseManager:

    def __init__(self):
        now = datetime.now().astimezone()
        self.date_from = now - timedelta(days=3)

    def get_games_to_update(self) -> QuerySet:
        return Game.objects.filter(
            report__isnull=True,
            status='Match Finished',
            game_date__gte=self.date_from,
        ).exclude(
            Q(home_team_stats__isnull=True) |
            Q(away_team_stats__isnull=True)
        ).select_related('home_team', 'away_team')

    def prepare_data(self, games_to_update: QuerySet) -> None:
        for game in games_to_update.iterator():
            home_team_data = TeamModel(**game.home_team.__dict__)
            away_team_data = TeamModel(**game.away_team.__dict__)
            home_team_stats = game.home_team_stats
            away_team_stats = game.away_team_stats
            report = Report(
                home_team_data,
                away_team_data,
                home_team_stats,
                away_team_stats,
            )
            game.report = report.create_report()

    def update_games(self, games_to_update: QuerySet) -> None:
        Game.objects.bulk_update(
            games_to_update,
            ['report'],
            batch_size=100,
        )
