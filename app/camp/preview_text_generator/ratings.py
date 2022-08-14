"""
Compare teams ratings.

"""

from camp.models import TeamModel

class Ratings:

    def __init__(self, home_team_data: TeamModel, away_team_data: TeamModel):
        self.home_team_name = home_team_data.name
        self.away_team_name = away_team_data.name
        self.home_defence = int(home_team_data.defence)
        self.home_attack = int(home_team_data.attack)
        self.away_defence = int(away_team_data.defence)
        self.away_attack = int(away_team_data.attack)
        self.team_a = home_team_data.name
        self.team_b = away_team_data.name
        self.defence_a = int(home_team_data.defence)
        self.attack_a = int(home_team_data.attack)
        self.defence_b = int(away_team_data.defence)
        self.attack_b = int(away_team_data.attack)

    def create_text(self):
        return ''
