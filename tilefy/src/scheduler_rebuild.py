"""rebuild jobs in scheduler"""

from src import scheduler


def rebuild():
    """rebuild"""
    handler = scheduler.TilefyScheduler()
    handler.clear_old()
    handler.setup_schedule()
