"""configure scheduled jobs"""

from os import environ

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.template import create_single_tile
from src.tilefy_redis import TilefyRedis
from src.watcher import watch_yml


class TilefyScheduler:
    """interact with scheduler"""

    CRON_DEFAULT = "0 0 * * *"

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=environ.get("TZ", "UTC"))
        self.add_job_store()
        self.tiles = self.get_tiles()

    def get_tiles(self):
        """get all tiles set in config"""
        config = TilefyRedis().get_message("config")
        if not config:
            print("no tiles defined in tiles.yml")
            return False

        return config["tiles"]

    def setup_schedule(self):
        """startup"""
        if not self.tiles:
            print("no tiles defined in tiles.yml")
            return

        jobs = self.build_jobs()
        self.add_jobs(jobs)
        self.add_watcher()

        if not self.scheduler.running:
            self.scheduler.start()

    def add_job_store(self):
        """add jobstore to scheudler"""
        self.scheduler.add_jobstore(
            "redis",
            jobs_key="tl:jobs",
            run_times_key="tl:run_times",
            host=environ.get("REDIS_HOST"),
            port=environ.get("REDIS_PORT"),
        )

    def clear_old(self):
        """remove old jobs before recreating"""
        if not self.scheduler.running:
            self.scheduler.start()

        all_jobs = self.scheduler.get_jobs()
        for job in all_jobs:
            print(job)
            if job.id == "watcher":
                continue
            self.scheduler.remove_job(job.id)

    def build_jobs(self):
        """build list of expected jobs"""
        jobs = []
        for idx, (tile_slug, tile_conf) in enumerate(self.tiles.items()):
            job = {
                "job_id": str(idx),
                "job_name": tile_slug,
                "tile_conf": tile_conf,
            }
            jobs.append(job)

        return jobs

    def add_jobs(self, jobs):
        """add jobs to scheduler"""
        for job in jobs:
            cron_tab = job["tile_conf"].get("recreate", self.CRON_DEFAULT)
            if cron_tab == "on_demand":
                continue

            job_name = job["job_name"]
            self.scheduler.add_job(
                create_single_tile,
                CronTrigger.from_crontab(cron_tab),
                id=job["job_id"],
                name=job_name,
                args=[job_name, job["tile_conf"]],
                jitter=15,
                replace_existing=True,
            )
            print(f"{job_name}: Add job {cron_tab}")

    def add_watcher(self):
        """add watcher to jobs"""
        self.scheduler.add_job(
            watch_yml,
            "interval",
            seconds=5,
            id="watcher",
            replace_existing=True,
        )
