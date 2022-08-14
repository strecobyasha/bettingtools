"""
Main file for crontab to parse data from the API.

"""

import time

from logs.logger import scout_logger as logger
from scout import (update_events, update_lineups, update_odds, update_scores,
                   update_standings, update_stats)


def updaters():
    logger.info('Scout launched.')
    update_scores.updater()
    update_odds.updater()
    # The API has limitations on the number of requests per minute.
    # So, we need to pause the script after the most expensive part.
    time.sleep(90)
    update_stats.updater()
    update_events.updater()
    update_lineups.updater()
    update_standings.updater()
    logger.info('Scout has completed.')
