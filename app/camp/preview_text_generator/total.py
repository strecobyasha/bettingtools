"""
Total goals expectations.

"""

class Total:

    def __init__(self, odds: dict):
        self.odds = odds
        self.total_under_odds = '{:.2f}'.format(self.odds.get('Under 2.5')[-1])
        self.total_over_odds = '{:.2f}'.format(self.odds.get('Over 2.5')[-1])
        self._game = ['match', 'game', 'clash', 'fixture']

    def create_text(self) -> str:
        return ''
