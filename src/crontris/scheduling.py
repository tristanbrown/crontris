"""Scheduler"""
import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.base import JobLookupError

from .settings import Config
from .messaging import RpcClient

logger = logging.getLogger(__name__)

class Scheduler(BackgroundScheduler):
    def __init__(self):
        ## Choose the database for the jobs queue.
        jobstores = {
            'default': MongoDBJobStore(
                database=Config.DATABASE_NAME,
                collection=f"jobs_{Config.APP_HOST}",
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                username=Config.USERNAME,
                password=Config.PASSWORD,
                authSource='admin',
                )}
        ## Use threads for unlimited simultaneous messages.
        executors = {'default': ThreadPoolExecutor(max_workers=50)}
        ## Combine identical messages.
        job_defaults = {'coalesce': True, 'max_instances': 1, 'misfire_grace_time': 15,}
        super().__init__(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
        )

    @classmethod
    def consume(cls, message):
        """Receives a json-formatted message.

        The 'method' key should refer to a class method.
        The remaining key:value pairs will be passed as kwargs to the method.
        """
        logger.debug(f"Message received by scheduler: {message}")
        method = message.pop('method')
        call = getattr(cls, method)
        return call(**message)

    @staticmethod
    def forward(body):
        rpc = RpcClient()
        result = rpc.call(body)
        return result

    def active(self, dbid):
        """Boolean value of whether the Study is active in the scheduler."""
        return bool(self.get_job(dbid))

    def activate(self, dbid, repeat, name):
        """Periodically run the Study."""
        self.add_job(
            self.forward,
            args=[dbid],
            trigger='interval',
            seconds=repeat,
            id=dbid,
            name=name,
            replace_existing=True,
            next_run_time=datetime.datetime.now()
        )

    def deactivate(self, dbid):
        """Stop the Study from running periodically."""
        try:
            self.remove_job(dbid)
            self.remove_job(dbid + '_waiting')
        except JobLookupError:
            print("Job not found")

    def run_study_once(self, dbid, name, force=False):
        """Submit a job to run the whole Study once."""
        self.add_job(
            self.forward,
            args=[dbid, force],
            id=dbid + '_once',
            name=name + ' once',
            replace_existing=False,
        )

    def rename(self, dbid, name):
        """Rename the Study."""
        self.modify_job(dbid, name=name)

    def reschedule(self, dbid, repeat):
        """Update the valid age for the data."""
        self.reschedule_job(dbid, trigger='interval', seconds=repeat)
