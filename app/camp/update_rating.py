"""
Update and set team rating.

Fill teams ratings fields for each not started game.
Update teams ratings after the end of the games.

"""

from camp.ratings.games_manager import GamesManager
from camp.ratings.teams_manager import TeamsManager


def updater():
    games_manager = GamesManager()
    teams_manager = TeamsManager()

    future_games = games_manager.get_future_games()
    finished_games = games_manager.get_finished_games()

    games_manager.prepare_data(future_games)
    games_manager.update_games(future_games)

    teams_to_update = teams_manager.collect_teams(finished_games)
    teams_manager.update_teams(teams_to_update)
