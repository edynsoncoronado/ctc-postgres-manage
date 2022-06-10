import os

from tasks import db_manage

from celery import Celery
from celery.schedules import crontab


celery = Celery(
    __name__,
    broker=os.environ.get(
        'CELERY_BROKER_URL', 'redis://redis:6379/0'
    ),
    backend=os.environ.get(
        'CELERY_RESULT_BACKEND', 'redis://redis:6379/0'
    )
)

@celery.task(name="db_manage_backup")
def db_manage_backup():
    db_manage.execute_main('backup')
    return True

@celery.task(name="db_manage_restore1")
def db_manage_restore1():
    db_manage.execute_main('restore1')
    return True

@celery.task(name="db_manage_restore2")
def db_manage_restore2():
    db_manage.execute_main('restore2')
    return True

@celery.task(name="db_manage_restore3")
def db_manage_restore3():
    db_manage.execute_main('restore3')
    return True

celery.conf.beat_schedule = {
    'db_manage_backup': {
        'task': "db_manage_backup",
        'schedule': crontab(hour=22, minute=50)
    },
}
