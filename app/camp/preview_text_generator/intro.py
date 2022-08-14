"""
Preview intro text.

"""

from camp.models import TeamModel, TourModel

class Intro:

    def __init__(
            self,
            tour_data: TourModel,
            home_team_data: TeamModel,
            away_team_data: TeamModel,
            game_date: str,
            game_time: str,
            stadium: str,
    ):
        self.tour_data = tour_data
        self.home_team_data = home_team_data
        self.away_team_data = away_team_data
        self.game_date = game_date
        self.game_time = game_time
        self.stadium = stadium

    def create_text(self) -> str:
        return ''
