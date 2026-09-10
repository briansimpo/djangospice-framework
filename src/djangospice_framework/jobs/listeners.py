from djangospice_framework.core.payload import Payload
from djangospice_framework.events import EventListener, listen

from .broadcast import broadcast_event
from .events import (
    JobCompletedEvent,
    JobEvent,
    JobFailedEvent,
    JobProgressedEvent,
    JobStartedEvent,
)


@listen(JobStartedEvent)
@listen(JobProgressedEvent)
@listen(JobCompletedEvent)
@listen(JobFailedEvent)
class JobEventListener(EventListener):

    should_queue = True
    queue_name = "job-notifications"

    retry_on = (ConnectionResetError, TimeoutError)
    max_retries = 5
    retry_backoff = 30

    def handle(self, event: JobEvent) -> None:
        payload = Payload()

        if isinstance(event, JobProgressedEvent):
            payload.set("message", event.message)
            payload.set("extra", event.extra)

        elif isinstance(event, JobCompletedEvent):
            payload.set("result", event.result)

        elif isinstance(event, JobFailedEvent):
            payload.set("error", event.error)

        broadcast_event(
            event=event,
            data=payload.to_dict(),
        )