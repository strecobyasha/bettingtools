"""
Get standings.

Parse API standings for each tournament, that is running.
"""

from scout.parsers import StandingsParser
from scout.updaters import StandingsUpdater
from scout.updates_managers import StandingsUpdatesManager


def updater() -> None:
    standings_updater = StandingsUpdater()
    standings_parser = StandingsParser(url_tail='standings')
    updates_manager = StandingsUpdatesManager(
        updater=standings_updater,
        parser=standings_parser,
    )
    updates_manager.start_updating()
