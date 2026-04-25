import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

parser_scheduler = BackgroundScheduler()


def run_vk_parser_job() -> None:
    try:
        from . import vk_parser

        logger.info("VK parser job started")
        vk_parser.main()
        logger.info("VK parser job finished")
    except Exception:
        logger.exception("VK parser job failed")


def start_vk_parser_scheduler() -> None:
    if not os.getenv("VK_TOKEN"):
        logger.warning("VK_TOKEN is not set, VK parser scheduler was not started")
        return

    if parser_scheduler.running:
        return

    interval_minutes = 10

    parser_scheduler.add_job(
        func=run_vk_parser_job,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=5),
        id="vk_parser_startup",
        replace_existing=True,
        max_instances=1,
    )
    parser_scheduler.add_job(
        func=run_vk_parser_job,
        trigger="interval",
        minutes=interval_minutes,
        id="vk_parser_interval",
        replace_existing=True,
        max_instances=1,
    )
    parser_scheduler.start()
    logger.info("VK parser scheduler started, interval=%s minutes", interval_minutes)
