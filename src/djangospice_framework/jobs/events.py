from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from djangospice_framework.events import BaseEvent

from .base import Job


@dataclass(frozen=True, slots=True)
class JobEvent(BaseEvent):
    """Base event for job lifecycle events."""
    job: Job


@dataclass(frozen=True, slots=True)
class JobQueuedEvent(JobEvent):
    name = "job.queued"


@dataclass(frozen=True, slots=True)
class JobStartedEvent(JobEvent):
    name = "job.started"


@dataclass(frozen=True, slots=True)
class JobProgressedEvent(JobEvent):
    name = "job.progressed"
    message: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class JobCompletedEvent(JobEvent):
    name = "job.completed"
    result: Any = None


@dataclass(frozen=True, slots=True)
class JobFailedEvent(JobEvent):
    name = "job.failed"
    error: str = ""