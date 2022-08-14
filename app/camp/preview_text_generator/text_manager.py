"""
Preview text manager.

Create texts about current game, teams last games,
compare ratings and chances.

"""

from camp.models import GameModel, TeamModel, TourModel

from .chances import Chances
from .intro import Intro
from .last_games import LastGames
from .ratings import Ratings
from .total import Total


class Preview:

    def __init__(
            self,
            game_data: GameModel,
            tour_data: TourModel,
            home_team_data: TeamModel,
            away_team_data: TeamModel,
            home_team_last_games: dict,
            away_team_last_games: dict,
    ):
        self.game_data = game_data
        self.tour_data = tour_data
        self.home_team_data = home_team_data
        self.away_team_data = away_team_data
        self.home_team_last_games = home_team_last_games
        self.away_team_last_games = away_team_last_games

    def create_preview(self) -> dict:
        game_date = self.game_data.game_date.strftime('%B %d')
        game_time = self.game_data.game_date.strftime('%H:%M')
        stadium = self.game_data.venue

        intro = Intro(
            tour_data=self.tour_data,
            home_team_data=self.home_team_data,
            away_team_data=self.away_team_data,
            game_date=game_date,
            game_time=game_time,
            stadium=stadium,
        ).create_text()

        chances = Chances(
            home_team_data=self.home_team_data,
            away_team_data=self.away_team_data,
            odds=self.game_data.game_outcome_odds,
        ).create_text()

        total = Total(
            odds=self.game_data.game_total_odds,
        ).create_text()

        home_team_last_games = ''
        if len(self.home_team_last_games['last_games']) > 0:
            home_team_last_games = LastGames(
                team_data=self.home_team_data,
                last_games=self.home_team_last_games['last_games'],
            ).create_text()

        away_team_last_games = ''
        if len(self.away_team_last_games['last_games']) > 0:
            away_team_last_games = LastGames(
                team_data=self.away_team_data,
                last_games=self.away_team_last_games['last_games'],
            ).create_text()

        ratings = Ratings(
            home_team_data=self.home_team_data,
            away_team_data=self.away_team_data,
        ).create_text()

        return {
            'intro': intro,
            'chances': chances,
            'total': total,
            'home_team_last_games': home_team_last_games,
            'away_team_last_games': away_team_last_games,
            'ratings': ratings,
        }
