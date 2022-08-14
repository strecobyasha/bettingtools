"""
Predictions generator.

"""

import json
import math
from copy import deepcopy
from itertools import chain, combinations, combinations_with_replacement

import pandas as pd
from sklearn.preprocessing import StandardScaler


class Predictor:

    def __init__(self, model):
        self.model = model

    @classmethod
    def prepare_data(cls, ds, test=None):
        # Prepare dataset.
        home_defence = ds['home_team_defence']
        home_attack = ds['home_team_attack']
        away_defence = ds['away_team_defence']
        away_attack = ds['away_team_attack']
        # tour_av_goals = ds['tournament__av_goals_number']
        home_win_prob = round(1/ds['home_odds_end'], 3)
        away_win_prob = round(1/ds['away_odds_end'], 3)

        defence = pd.concat([away_defence, home_defence])
        attack = pd.concat([home_attack, away_attack])
        prob = pd.concat([home_win_prob, away_win_prob])
        # tour_av_goals_double = pd.concat([tour_av_goals, tour_av_goals])

        x = pd.DataFrame()
        x.insert(0, 'attack', attack)
        x.insert(1, 'attack/defence', attack/defence)
        # x.insert(1, 'tour goals', tour_av_goals_double)
        x.insert(2, 'prob', prob)

        scale = StandardScaler()
        x = scale.fit_transform(x)

        if test:
            home_goals = ds['home_goals_ft']
            away_goals = ds['away_goals_ft']
            goals = pd.concat([home_goals, away_goals])

            y = pd.DataFrame()
            y.insert(0, 'goals', goals)
            y = y.to_numpy()
        
        if test:
            return x, y
        
        return x

    def predict_goals(self, games_set):
        dataset = self.prepare_data(games_set)
        predictions = self.model.predict(dataset)

        # for i in range(len(games_set.values)):
        for i in range(len(games_set)):
            # Predict, how many goals will score teams (float numbers).
            home_goals_pred = predictions[i]
            away_goals_pred = predictions[i+len(games_set)]
            # Odds
            home_win_odds = games_set.iloc[i]['home_odds_end']
            draw_odds = games_set.iloc[i]['draw_odds_end']
            away_win_odds = games_set.iloc[i]['away_odds_end']
            total_under_odds = games_set.iloc[i]['under_odds_end']
            total_over_odds = games_set.iloc[i]['over_odds_end']
            # Outcome probability.
            home_win_prob, draw_prob, away_win_prob,\
            total_under_prob, total_over_prob = self.calculate_outcome_prob(
                home_goals_pred, away_goals_pred)
            # Get outcome prediction
            outcome_prediction, handicap_prediction = self.predict_outcome(
                home_win_prob, draw_prob, away_win_prob, home_win_odds, draw_odds, away_win_odds,
            )
            # Get total prediction
            total_prediction = self.predict_total(
                total_under_prob, total_over_prob, total_under_odds, total_over_odds,
            )

            # print(
            #     str(games_set.iloc[i]['home_team_defence']).ljust(5),
            #     str(games_set.iloc[i]['home_team_attack']).ljust(5),
            #     str(games_set.iloc[i]['away_team_defence']).ljust(5),
            #     str(games_set.iloc[i]['away_team_attack']).ljust(5),
            #     str(round(games_set.iloc[i]['home_team_attack']/games_set.iloc[i]['away_team_defence'], 3)).ljust(7),
            #     str(round(games_set.iloc[i]['away_team_attack']/games_set.iloc[i]['home_team_defence'], 3)).ljust(7),
            #     str(games_set.iloc[i]['tournament__av_goals_number']).ljust(7),
            #     f"{round(100/home_win_odds, 1)} / {round(100/draw_odds, 1)} / {round(100/away_win_odds, 1)}".ljust(22),
            #     f"{round(home_win_prob*100, 1)} / {round(draw_prob*100, 1)} / {round(away_win_prob*100, 1)}".ljust(22),
            #     f"{round(float(home_goals_pred), 3)} : {round(float(away_goals_pred), 3)}".ljust(15),
            #     f"{games_set.iloc[i]['home_goals_ft']}:{games_set.iloc[i]['away_goals_ft']}".ljust(5),
            #     outcome_prediction
            #     )

            yield {
                'api_game_id': int(games_set.iloc[i]['api_game_id']),
                'outcome_pred': outcome_prediction,
                'handicap_pred': handicap_prediction,
                'total_pred': total_prediction,
                'home_win_pob': round(home_win_prob*100, 1),
                'draw_pob': round(draw_prob*100, 1),
                'away_win_pob': round(away_win_prob*100, 1),
                'total_under_prob': round(total_under_prob*100, 1),
                'total_over_prob': round(total_over_prob*100, 1),
                'home_goals_pred': float(home_goals_pred),
                'away_goals_pred': float(away_goals_pred),
                'home_goals_prob': [round(float(x[0]), 3) for x in home_goals_prob],
                'away_goals_prob': [round(float(x[0]), 3) for x in away_goals_prob],
                }

    def calc_prob(self, condition: str) -> float:
        return float(sum(list(map(
            lambda x: home_goals_prob[x[0]] * away_goals_prob[x[1]]
            if eval(condition) else 0,
            deepcopy(all_scores)
        ))))

    def calculate_outcome_prob(self, home_goals_pred: float, away_goals_pred: float) -> tuple:
        # Team goals probability (from 0 to 9), based on Poisson distribution.
        global home_goals_prob, away_goals_prob, all_scores
        home_goals_prob = []
        away_goals_prob = []
        f = 1
        for g in range(10):
            if g > 1:
                f = f * g
            home_goals_prob.append(pow(math.e, -home_goals_pred) * pow(home_goals_pred, g) / f)
            away_goals_prob.append(pow(math.e, -away_goals_pred) * pow(away_goals_pred, g) / f)
        # Score combinations.
        all_scores = chain(combinations_with_replacement([i for i in range(10)], 2),
                           combinations([i for i in range(9, -1, -1)], 2))
        # Outcome probability.
        home_win_prob = self.calc_prob('x[0] > x[1]')
        draw_prob = self.calc_prob('x[0] == x[1]')
        away_win_prob = self.calc_prob('x[1] > x[0]')
        # Total probability.
        total_under_prob = self.calc_prob('x[0] + x[1] < 3')
        total_over_prob = self.calc_prob('x[0] + x[1] > 2')

        return home_win_prob, draw_prob, away_win_prob, total_under_prob, total_over_prob

    def predict_outcome(
            self,
            home_win_prob: float,
            draw_prob: float,
            away_win_prob: float,
            home_win_odds: float,
            draw_odds: float,
            away_win_odds: float,
    ) -> tuple:
        home_win_ratio = round(home_win_prob/(1/home_win_odds), 2)
        draw_ratio = round(draw_prob/(1/draw_odds), 2)
        away_win_ratio = round(away_win_prob/(1/away_win_odds), 2)

        most_pred_probable_outcome = max(home_win_prob, draw_prob, away_win_prob)
        most_underestimated_outcome = max(home_win_ratio, draw_ratio, away_win_ratio)
        most_probable_outcome = min(home_win_odds, draw_odds, away_win_odds)

        if home_win_ratio == most_underestimated_outcome and home_win_ratio > 0.95 and home_win_odds < 3.5:
            # If home win outcome is the most underestimated.
            return 'Home win', self.handicap_prediction('Home win', home_win_odds)
        elif away_win_ratio == most_underestimated_outcome and away_win_ratio > 0.95 and away_win_odds < 3.5:
            # If away win outcome is the most underestimated.
            return 'Away win', self.handicap_prediction('Away win', away_win_odds)
        elif draw_ratio > 0.8 and draw_odds < 4:
            # If draw ration is acceptable and draw odds is now too big.
            if home_win_odds > away_win_odds:
                handicap_pred = self.handicap_prediction('Home win', home_win_odds)
            else:
                handicap_pred = self.handicap_prediction('Away win', away_win_odds)
            return 'Draw', handicap_pred
        # Else return the most probable outcome.
        outcomes = {0: 'Home win', 1: 'Draw', 2: 'Away win'}
        outcome_pred = outcomes[[home_win_prob, draw_prob, away_win_prob].index(most_pred_probable_outcome)]
        # outcome_pred = outcomes[[home_win_ratio, draw_ratio, away_win_ratio].index(most_underestimated_outcome)]
        match outcome_pred:
            case 'Home win':
                handicap_pred = self.handicap_prediction('Away win', away_win_odds)
            case 'Away win':
                handicap_pred = self.handicap_prediction('Away win', away_win_odds)
            case _:
                if home_win_odds > away_win_odds:
                    handicap_pred = self.handicap_prediction('Home win', home_win_odds)
                else:
                    handicap_pred = self.handicap_prediction('Away win', away_win_odds)

        return outcome_pred, handicap_pred

    def handicap_prediction(self, prediction: str, odds: float) -> str:
        if odds < 1.3:
            return f'{prediction} (-2.5)'
        elif odds < 1.5:
            return f'{prediction} (-1.5)'
        elif odds < 1.8:
            return f'{prediction} (-1)'
        elif odds < 2.1:
            return f'{prediction} (-0.25)'
        elif odds < 2.5:
            return f'{prediction} (0)'
        return f'{prediction} (+0.5)'

    def predict_total(
            self,
            total_under_prob: float,
            total_over_prob: float,
            total_under_odds: float,
            total_over_odds: float,
    ) -> str:
        total_under_ratio = round(total_under_prob/(1/total_under_odds), 2)
        total_over_ratio = round(total_over_prob/(1/total_over_odds), 2)

        most_pred_probable_total = max(total_under_prob, total_over_prob)
        most_underestimated_total = max(total_under_ratio, total_over_ratio)
        most_probable_total = min(total_under_odds, total_over_odds)

        totals = {0: 'Total under 2.5', 1: 'Total over 2.5'}

        if total_under_ratio == most_underestimated_total and total_under_ratio > 0.95:
            # If total under 2.5 goals is the most underestimated.
            return 'Total under 2.5'
        elif total_over_ratio == most_underestimated_total and total_over_ratio > 0.95:
            # If total over 2.5 goals is the most underestimated.
            return 'Total over 2.5'
        # Else return the most probable total.
        return totals[[total_under_prob, total_over_prob].index(most_pred_probable_total)]
        # return totals[[total_under_prob, total_over_prob].index(most_probable_total)]
