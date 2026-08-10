from celery import Celery

from src.core.config import settings


def build_celery_app() -> Celery:
    """Build the process-wide Celery application.

    Config lives here so it stays testable/inspectable via the factory,
    same as `core.redis.client.init_redis`; the module-scope `celery_app`
    below exists only because Celery's own CLI (`celery -A
    src.core.jobs.celery_app:celery_app worker`) needs a statically
    importable instance to target, the same concession `main.py` makes
    for uvicorn with `app = create_app()`.
    """
    app = Celery("lumiere", broker=settings.CELERY_BROKER_URL)
    app.conf.update(
        task_ignore_result=True,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_default_queue="default",
        # Ack after execution (not on receipt) so a worker crash mid-task
        # requeues it instead of losing it; paired with prefetch=1 so one
        # worker can't hoard tasks off the broker while others sit idle.
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
        task_default_retry_delay=settings.CELERY_TASK_DEFAULT_RETRY_DELAY,
        task_default_max_retries=settings.CELERY_TASK_MAX_RETRIES,
        # Cheap to enable, makes `celery events`/`celery inspect active`
        # usable ad hoc without adding a Flower/APM service to the stack.
        task_send_sent_event=True,
        worker_send_task_events=True,
    )
    # Explicit list, not a wildcard scan — mirrors composition/container.py
    # listing each module by name rather than scanning modules/*. These are
    # *string* package paths: core/jobs must never gain a Python import
    # dependency on modules/*.
    app.autodiscover_tasks(
        [
            # related_name="tasks" imports "<package>.tasks" for each entry
            # below, so the string must resolve to <module>.transport.tasks.
            "src.modules.email.transport",
        ],
        related_name="tasks",
    )
    return app


celery_app = build_celery_app()
