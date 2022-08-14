import logging
from pathlib import Path

path = Path(__file__).resolve().parent

logging.basicConfig(
    filename=''.join([str(path), '/logfile.log']),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

scout_logger = logging.getLogger('SCOUT')
camp_logger = logging.getLogger('CAMP')
