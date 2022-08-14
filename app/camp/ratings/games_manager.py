"""
Read and write games.

Collect games from the database:
not started games to assign teams ratings;
finished games to recalculate teams ratings.

"""

from datetime import datetime, timedelta

from django.db.models import QuerySet

from arena.models import Game
from camp.ratings.calculate_rating import RatingCalculator


class GamesManager:

    def __init__(self):
        now = datetime.now().astimezone()
        self.date_from = now - timedelta(days=1)
        self.date_to = now + timedelta(days=3)

    def get_future_games(self) -> QuerySet:
        return Game.objects.filter(
            status='Not Started',
            game_date__lte=self.date_to,
        ).select_related('home_team', 'away_team', 'tournament')

    def get_finished_games(self) -> QuerySet:
        return Game.objects.filter(
            status='Match Finished',
            game_date__gte=self.date_from,
        ).select_related('home_team', 'away_team', 'tournament')

    def prepare_data(self, future_games: QuerySet) -> None:
        for game in future_games:
            game.home_team_defence, game.home_team_attack = RatingCalculator.get_rating(
                game.home_team,
                game.tournament,
                game.game_date,
            )
            game.away_team_defence, game.away_team_attack = RatingCalculator.get_rating(
                game.away_team,
                game.tournament,
                game.game_date
            )

    def update_games(self, future_games: QuerySet) -> None:
        Game.objects.bulk_update(
            future_games,
            ['home_team_defence', 'home_team_attack', 'away_team_defence', 'away_team_attack'],
            batch_size=100,
        )
