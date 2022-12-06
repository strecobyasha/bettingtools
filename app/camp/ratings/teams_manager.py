"""
Read and write teams.

Collect teams from the database to update ratings.

"""

from django.db.models import QuerySet

from arena.models import Team
from camp.ratings.calculate_rating import RatingCalculator


class TeamsManager:

    def collect_teams(self, finished_games: QuerySet) -> list:
        teams_to_update = []
        for game in finished_games.iterator():
            home_team = game.home_team
            away_team = game.away_team
            # If team ratings were not updated yet.
            if home_team.rating_updated < game.game_date:
                home_rating = {
                    'defence': game.home_team_defence,
                    'attack': game.home_team_attack,
                }
                away_rating = {
                    'defence': game.away_team_defence,
                    'attack': game.away_team_attack,
                }
                # If ratings were set for the game and they are not None.
                if home_rating['defence'] != None and away_rating['defence'] != None:
                    new_ratings = RatingCalculator.calculate_rating(
                        home_rating,
                        away_rating,
                        game.home_goals_ft,
                        game.away_goals_ft,
                        game.tournament.av_goals_number,
                    )

                    home_team.defence = new_ratings['home_defence']
                    home_team.attack = new_ratings['home_attack']
                    home_team.rating_updated = game.game_date

                    away_team.defence = new_ratings['away_defence']
                    away_team.attack = new_ratings['away_attack']
                    away_team.rating_updated = game.game_date

                    teams_to_update.extend([home_team, away_team])

        return teams_to_update

    def update_teams(self, teams_to_update: list) -> None:
        Team.objects.bulk_update(
            teams_to_update,
            ['defence', 'attack', 'rating_updated'],
            batch_size=100,
        )
