"""
Collect games data from DB.

Collect data for machine learning.

"""

from datetime import datetime, timedelta

import pandas as pd
from django.db.models import Q
from django.db.models.fields.json import KeyTextTransform

from arena.models import Game

# Time offset in hours for collecting games to create previews.
OFFSET = 48

class Collector:

    def __init__(self):
         self.games_data = pd.DataFrame()

    def learning_dataset(self) -> None:
        # Collect games from DB for machine learning.
        self.games_data = pd.DataFrame(
            Game.objects.filter(status='Match Finished').exclude(
                Q(home_team_defence__isnull=True) |
                Q(away_team_defence__isnull=True) |
                Q(game_odds__isnull=True)).values(
                'api_game_id',
                'home_team_defence',
                'home_team_attack',
                'away_team_defence',
                'away_team_attack',
                'tournament__av_goals_number',
                'home_goals_ft',
                'away_goals_ft',
            ).annotate(
                outcome_odds=KeyTextTransform('Match Winner', 'game_odds'),
                total_odds=KeyTextTransform('Goals Over/Under', 'game_odds'),
            ).order_by('-game_date')[:30000]
        )

    def prediction_dataset(self) -> None:
        now = datetime.now().astimezone()
        date_to = now + timedelta(hours=OFFSET)
        self.games_data = pd.DataFrame(
            Game.objects.filter(
                preview__isnull=True,
                status='Not Started',
                pub_date__lte=date_to,
            ).exclude(
                Q(home_team_defence__isnull=True) |
                Q(away_team_defence__isnull=True) |
                Q(game_odds__isnull=True)).values(
                'api_game_id',
                'home_team_defence',
                'home_team_attack',
                'away_team_defence',
                'away_team_attack',
            ).annotate(
                outcome_odds=KeyTextTransform('Match Winner', 'game_odds'),
                total_odds=KeyTextTransform('Goals Over/Under', 'game_odds'),
            )
        )

    def process_data(self) -> pd.DataFrame:
        outcome_odds_set = pd.json_normalize(self.games_data['outcome_odds'])
        outcome_odds_set[['home_odds_start', 'home_odds_end']] = pd.DataFrame(
            outcome_odds_set.Home.tolist(), index=outcome_odds_set.index,
        )
        outcome_odds_set[['draw_odds_start', 'draw_odds_end']] = pd.DataFrame(
            outcome_odds_set.Draw.tolist(), index=outcome_odds_set.index,
        )
        outcome_odds_set[['away_odds_start', 'away_odds_end']] = pd.DataFrame(
            outcome_odds_set.Away.tolist(), index=outcome_odds_set.index,
        )

        total_odds_set = pd.json_normalize(self.games_data['total_odds'])
        total_odds_set[['under_odds_start', 'under_odds_end']] = pd.DataFrame(
            total_odds_set['Under 2.5'].tolist(), index=total_odds_set.index,
        )
        total_odds_set[['over_odds_start', 'over_odds_end']] = pd.DataFrame(
            total_odds_set['Over 2.5'].tolist(), index=total_odds_set.index,
        )

        data_set = outcome_odds_set.join(total_odds_set).join(self.games_data)
        data_set = data_set[
            (data_set['home_odds_end'] != 1) & (data_set['away_odds_end'] != 1) &
            (data_set['under_odds_end'] != 1) & (data_set['over_odds_end'] != 1)
        ]
        data_set = data_set.drop(
            columns=['outcome_odds', 'total_odds']
        )

        return data_set
