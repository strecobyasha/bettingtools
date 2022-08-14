"""
Report text manager.

Compare teams stats after the match has finished.

"""

import random
from typing import Any

from camp.models import TeamModel
from camp.utils.team_name import get_team_name


class Report:
    def __init__(
            self,
            home_team_data: TeamModel,
            away_team_data: TeamModel,
            home_team_stats: dict,
            away_team_stats: dict,
    ):
        self.home_team_data = home_team_data
        self.away_team_data = away_team_data
        self.home_team_stats = home_team_stats
        self.away_team_stats = away_team_stats
        self.home_team_facts = []
        self.away_team_facts = []
        self._game = ['match', 'game', 'clash', 'fixture']
        self._shots = ['shots', 'attempts']

    def create_report(self) -> dict:
        funcs = {
            'Total Shots': self.total_shots_text,
            'Shots on Goal': self.shots_on_goal_text,
            'Shots insidebox': self.shots_insidebox_text,
            'Shots outsidebox': self.shots_outsidebox_text,
            'Blocked Shots': self.blocked_shots_text,
            'Ball Possession': self.ball_possession_text,
            'Total passes': self.total_passes_text,
            'Passes accurate': self.passes_accurate_text,
            'Passes %': self.passes_ratio_text,
            'Corner Kicks': self.corners_text,
            'Fouls': self.fouls_text,
            'Offsides': self.offsides_text,
        }
        for k, v in self.home_team_stats.items():
            if k in funcs:
                team = get_team_name(self.home_team_data)
                v1 = self.convert_stats_value(v)
                v2 = self.convert_stats_value(self.away_team_stats[k])
                if v1 < v2:
                    team = get_team_name(self.away_team_data)
                    v1, v2 = v2, v1
                    self.away_team_facts.append(funcs[k](team, v1, v2))
                else:
                    self.home_team_facts.append(funcs[k](team, v1, v2))

        return {
            'home_team': self.home_team_facts,
            'away_team': self.away_team_facts,
        }

    def convert_stats_value(self, v: Any) -> int:
        # Convert stats value into integer.
        if type(v) is str and '%' in v:
            return int(v.replace('%', ''))
        if v is None or v == 'None' or v == '':
            return 0

        return int(v)

    def total_shots_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def shots_on_goal_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def shots_insidebox_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def shots_outsidebox_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def blocked_shots_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def ball_possession_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def total_passes_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def passes_accurate_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def passes_ratio_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def corners_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def fouls_text(self, team: str, v1: int, v2: int) -> str:
        return ''

    def offsides_text(self, team: str, v1: int, v2: int) -> str:
        return ''
