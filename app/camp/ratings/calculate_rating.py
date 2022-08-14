"""
Functions for update_rating script.

calculate_rating - ratings after game ends for home and away team.
get_rating - pre-game ratings for home and away team.

"""

from datetime import datetime, timedelta


class RatingCalculator:

    @classmethod
    def calculate_rating(
        cls,
        home_rating: dict,
        away_rating: dict,
        home_goals: int,
        away_goals: int,
        tour_av_goals: float,
    ) -> dict:

        # Expected number of goals.
        home_goals_exp = tour_av_goals * (home_rating['attack'] / away_rating['defence'])
        away_goals_exp = tour_av_goals * (away_rating['attack'] / home_rating['defence'])

        # Part of rating for each goal under or over expected number.
        home_goal_price = home_rating['attack'] * 0.05
        if home_goals > home_goals_exp:
            home_goal_price = away_rating['defence'] * 0.05

        away_goal_price = away_rating['attack'] * 0.05
        if away_goals > away_goals_exp:
            away_goal_price = home_rating['defence'] * 0.05

        # Rating changes.
        home_score_calc = min((home_goals - home_goals_exp) * home_goal_price, home_goal_price * 3)
        away_score_calc = min((away_goals - away_goals_exp) * away_goal_price, away_goal_price * 3)

        # Set new ratings.
        home_new_defence = home_rating['defence'] - away_score_calc
        home_new_attack = home_rating['attack'] + home_score_calc
        away_new_defence = away_rating['defence'] - home_score_calc
        away_new_attack = away_rating['attack'] + away_score_calc

        return {'home_defence': round(home_new_defence, 1),
                'home_attack': round(home_new_attack, 1),
                'away_defence': round(away_new_defence, 1),
                'away_attack': round(away_new_attack, 1),
                }

    @classmethod
    def get_rating(cls, team: object, tour: object, date: datetime) -> tuple:
        # If rating was't set or it was updated too long ago - set base rating or return None.
        rating_relevance = team.rating_updated and (date - team.rating_updated).days < 90
        if (team.defence == 0 or not rating_relevance):
            if tour.is_championship:
                team.defence = tour.base_rating
                team.attack = tour.base_rating
                # Set 10 days to prevent a situation, when we have another
                # game for this team, that will take place earlier.
                team.rating_updated = date - timedelta(days=10)
                team.save()
            return None, None

        return team.defence, team.attack
