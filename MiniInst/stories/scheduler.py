import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from django.conf import settings
from .models.story import Story

logger = logging.getLogger(__name__)

scheduler = None


def archive_expired_stories():
    try:
        now = timezone.now()

        expired_stories = Story.objects.filter(
            expires_at__lte=now,
            is_archived=False
        )

        count = expired_stories.count()

        if count > 0:
            expired_stories.update(is_archived=True)
            logger.info("Архівовано {} прострочених сторіс о {}".format(count, now))
        else:
            logger.debug("Немає прострочених сторіс для архівації о {}".format(now))

    except Exception as e:
        logger.error("Помилка при архівації сторіс: {}".format(e))


def start_scheduler():
    global scheduler

    if scheduler is not None:
        logger.warning("Планувальник вже запущений")
        return

    if settings.DEBUG and not getattr(settings, 'SCHEDULER_AUTOSTART', True):
        logger.info("Планувальник відключений в режимі DEBUG")
        return

    try:
        scheduler = BackgroundScheduler(
            timezone=settings.TIME_ZONE if hasattr(settings, 'TIME_ZONE') else 'UTC'
        )

        scheduler.add_job(
            func=archive_expired_stories,
            trigger=IntervalTrigger(minutes=10),
            id='archive_expired_stories',
            name='Archive Expired Stories',
            replace_existing=True,
            max_instances=1,
        )

        scheduler.start()

        logger.info("APScheduler запущений успішно")

        scheduler.add_job(
            func=archive_expired_stories,
            trigger='date',
            run_date=timezone.now() + timezone.timedelta(seconds=30),
            id='initial_archive_check',
            name='Initial Archive Check'
        )

    except Exception as e:
        logger.error("Помилка запуску планувальника: {}".format(e))


def stop_scheduler():
    global scheduler

    if scheduler is not None:
        try:
            scheduler.shutdown()
            scheduler = None
            logger.info("APScheduler зупинений")
        except Exception as e:
            logger.error("Помилка зупинки планувальника: {}".format(e))


def get_scheduler_status():
    global scheduler

    if scheduler is None:
        return "Не запущений"

    if scheduler.running:
        jobs = scheduler.get_jobs()
        return f"Запущений ({len(jobs)} завдань)"
    else:
        return "Зупинений"