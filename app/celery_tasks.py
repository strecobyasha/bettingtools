from celery import Celery

from config.components.configs import CELERY_CONFIG

celery = Celery(backend=CELERY_CONFIG.backend, broker=CELERY_CONFIG.broker)

@celery.task
def init_transfer():
    from camp.scheduler import updaters as camp_updaters
    from scout.scheduler import updaters as scout_updaters

    scout_updaters()
    camp_updaters()


@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(3600.0, init_transfer.s(), name='Update data every 60 minutes.')
