"""
Get games main data from the Api.

Make requests to the Api to get the next data:
- List of upcoming games.
- Latest games results.
"""

from scout.parsers import ScoresParser
from scout.updaters import ScoresUpdater
from scout.updates_managers import ScoresUpdatesManager


def updater() -> None:
    scores_updater = ScoresUpdater()
    scores_parser = ScoresParser(url_tail='fixtures')
    updates_manager = ScoresUpdatesManager(
        updater=scores_updater,
        parser=scores_parser,
    )
    updates_manager.start_updating()
