"""
Read and write games.

Collect games from the database to create preview for.
Initiate preview text generation.
Save previews in the database.

"""

from django.db.models import F, QuerySet
from pandas import DataFrame

from arena.models import Game
from camp.models import GameModel, TeamModel, TourModel
from camp.preview.last_games import get_team_last_games
from camp.preview_text_generator.text_manager import Preview


class DataBaseManager:

    def get_games_to_update(self, data_set: DataFrame) -> QuerySet:
        return Game.objects.filter(
            api_game_id__in=data_set['api_game_id'],
        ).annotate(
            home_team_name=F('home_team__name'),
            away_team_name=F('away_team__name'),
            home_team_short_name=F('home_team__short_name'),
            away_team_short_name=F('away_team__short_name'),
        ).select_related('home_team', 'away_team', 'tournament')

    def prepare_data(self, games_to_update: QuerySet, predictions_dict: dict) -> None:
        for game in games_to_update:
            game_data = GameModel(**game.__dict__)
            tour_data = TourModel(**game.tournament.__dict__)
            home_team_data = TeamModel(**game.home_team.__dict__)
            away_team_data = TeamModel(**game.away_team.__dict__)

            # Collect last games.
            home_team_last_games = get_team_last_games(team=game.home_team)
            away_team_last_games = get_team_last_games(team=game.away_team)
            home_team_last_same_games = get_team_last_games(
                team=game.home_team,
                team_class=game_data.home_team_class,
                opponent_class=game_data.away_team_class,
            )
            away_team_last_same_games = get_team_last_games(
                team=game.away_team,
                team_class=game_data.away_team_class,
                opponent_class=game_data.home_team_class,
            )
            home_team_last_tour_games = get_team_last_games(team=game.home_team, tournament=game.tournament)
            away_team_last_tour_games = get_team_last_games(team=game.away_team, tournament=game.tournament)

            # Generate preview text.
            preview = Preview(
                game_data,
                tour_data,
                home_team_data,
                away_team_data,
                home_team_last_games,
                away_team_last_games,
            )

            # Update model fields.
            game.prediction = predictions_dict[game.api_game_id]
            game.preview = preview.create_preview()
            game.home_team_last_games = home_team_last_games
            game.away_team_last_games = away_team_last_games
            game.home_team_last_same_games = home_team_last_same_games
            game.away_team_last_same_games = away_team_last_same_games
            game.home_team_last_tour_games = home_team_last_tour_games
            game.away_team_last_tour_games = away_team_last_tour_games

    def update_games(self, games_to_update: QuerySet) -> None:
        Game.objects.bulk_update(
            games_to_update,
            ['prediction', 'preview', 'home_team_last_games', 'away_team_last_games',
             'home_team_last_same_games', 'away_team_last_same_games',
             'home_team_last_tour_games', 'away_team_last_tour_games'],
            batch_size=100,
        )
