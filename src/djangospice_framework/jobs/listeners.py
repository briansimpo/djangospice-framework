from djangospice_framework.events import EventListener, listen

from .broadcast import broadcast_job
from .events import (
    JobEvent,
    JobStartedEvent,
    JobProgressedEvent,
    JobCompletedEvent,
    JobFailedEvent,
)


@listen(JobStartedEvent)
@listen(JobProgressedEvent)
@listen(JobCompletedEvent)
@listen(JobFailedEvent)
class JobListener(EventListener):

    should_queue = True
    queue_name = "job-notifications"

    retry_on = (ConnectionResetError, TimeoutError)
    max_retries = 5
    retry_backoff = 30

    def handle(self, event: JobEvent) -> None:
        data = {}

        if isinstance(event, JobProgressedEvent):
            data = {
                "message": event.message,
                "extra": event.extra,
            }

        elif isinstance(event, JobCompletedEvent):
            data = {
                "result": getattr(event.result, "value", event.result),
            }

        elif isinstance(event, JobFailedEvent):
            data = {
                "error": event.error,
            }

        broadcast_job(
            job=event.job,
            event=event,
            data=data,
        )