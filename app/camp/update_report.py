"""
Get list of games, that

1. Without report yet;
2. Already have finished.

"""

from camp.report.db_manager import DataBaseManager


def updater():
    db_manager = DataBaseManager()
    games_to_update = db_manager.get_games_to_update()
    db_manager.prepare_data(games_to_update)
    db_manager.update_games(games_to_update)
