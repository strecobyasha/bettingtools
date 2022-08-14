"""
Test predictions model.

"""

from camp.preview.predictor import Predictor


def test(model, games_set):
    predictor = Predictor(model)
    predictions = predictor.predict_goals(games_set)

    bets = {
        'outcome_bets': 0,
        'outcome_wins': 0,
        'outcome_profit': 0,
        'total_bets': 0,
        'total_wins': 0,
        'total_profit': 0,
        'home_win_preds': 0,
        'draw_preds': 0,
        'away_win_preds': 0,
        'total_under_preds': 0,
        'total_over_preds': 0,
        'home_goals_pred': 0,
        'away_goals_pred': 0,
        'home_goals_act': 0,
        'away_goals_act': 0,
        }

    for index, pred in enumerate(predictions):
        home_goals = games_set.iloc[index]['home_goals_ft']
        away_goals = games_set.iloc[index]['away_goals_ft']

        home_win_odds = games_set.iloc[index]['home_odds_end']
        draw_odds = games_set.iloc[index]['draw_odds_end']
        away_win_odds = games_set.iloc[index]['away_odds_end']
        total_under_odds = games_set.iloc[index]['under_odds_end']
        total_over_odds = games_set.iloc[index]['over_odds_end']

        outcome_pred_result = check_outcome_pred(
            pred['outcome_pred'], home_goals, away_goals, home_win_odds, draw_odds, away_win_odds,
        )
        if outcome_pred_result[0]:
            bets['outcome_wins'] += 1
            bets['outcome_profit'] += outcome_pred_result[1]

        total_pred_result = check_total_pred(
            pred['total_pred'], home_goals, away_goals, total_under_odds, total_over_odds,
        )
        if total_pred_result[0]:
            bets['total_wins'] += 1
            bets['total_profit'] += total_pred_result[1]

        bets['outcome_bets'] += 1
        bets['outcome_profit'] -= 1
        bets['total_bets'] += 1
        bets['total_profit'] -= 1
        bets['home_goals_pred'] += pred['home_goals_pred']
        bets['away_goals_pred'] += pred['away_goals_pred']
        bets['home_goals_act'] += home_goals
        bets['away_goals_act'] += away_goals
        bets[outcome_pred_result[2]] += 1
        bets[total_pred_result[2]] += 1

    return bets


def check_outcome_pred(pred, home_goals, away_goals, home_win_odds, draw_odds, away_win_odds):
    match pred:
        case 'Home win':
            return home_goals > away_goals, home_win_odds, 'home_win_preds'
        case 'Draw':
            return home_goals == away_goals, draw_odds, 'draw_preds'
        case 'Away win':
            return home_goals < away_goals, away_win_odds, 'away_win_preds'


def check_total_pred(pred, home_goals, away_goals, total_under_odds, total_over_odds):
    match pred:
        case 'Total under 2.5':
            return home_goals + away_goals < 3, total_under_odds, 'total_under_preds'
        case 'Total over 2.5':
            return home_goals + away_goals > 2, total_over_odds, 'total_over_preds'
