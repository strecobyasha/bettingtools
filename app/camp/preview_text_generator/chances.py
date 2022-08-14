"""
Odds comparison.

"""

from camp.models import TeamModel

class Chances:

    def __init__(self,
            home_team_data: TeamModel,
            away_team_data: TeamModel,
            odds: dict,
    ):
        self.home_team_data = home_team_data
        self.away_team_data = away_team_data
        self.odds = odds
        self.favourite = None
        self.underdog = None
        self.favourite_odds = self.odds.get('Home')[-1]
        self.underdog_odds = self.odds.get('Away')[-1]
        self.favourite_odds_str = '{:.2f}'.format(self.odds.get('Home')[-1])
        self.draw_odds_str = '{:.2f}'.format(self.odds.get('Draw')[-1])
        self.underdog_odds_str = '{:.2f}'.format(self.odds.get('Away')[-1])
        self._game = ['match', 'game', 'clash', 'fixture']
        self._reason = ['', 'According the odds ', 'According the bookies estimates ', 'Bookies believe that ']

    def create_text(self) -> str:
        return ''
