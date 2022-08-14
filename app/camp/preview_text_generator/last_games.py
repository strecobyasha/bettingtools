"""
Analyze team last games results.

"""

from camp.models import TeamModel

class LastGames:

    def __init__(self, team_data: TeamModel, last_games: list):
        self.team_data = team_data
        self.last_games = last_games

    def create_text(self) -> str:
        return ''
