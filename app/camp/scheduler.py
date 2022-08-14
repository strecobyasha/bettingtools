"""
Main file for crontab to update previews, reports and ratings.

"""

from camp import update_preview, update_rating, update_report
from logs.logger import camp_logger as logger


def updaters():
    logger.info('Camp launched.')
    update_preview.updater()
    update_rating.updater()
    update_report.updater()
    logger.info('Camp has completed.')
