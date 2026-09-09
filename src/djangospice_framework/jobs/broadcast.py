from __future__ import annotations

from typing import Any

from djangospice_framework.realtime.broadcast import Broadcast

from .base import Job

def broadcast_job(job: Job, event: str, data: dict[str, Any] | None = None) -> None:
    """
    Broadcast a job lifecycle event to job-specific and user-specific
    realtime channels.
    """
    if not getattr(job, "id", None):
        return

    payload = {
        "type": event,
        "job": job.to_dict(),
        **(data or {}),
    }

    # Broadcast to clients watching this specific job.
    Broadcast.group(
        group=f"job_{job.id}",
        data=payload, 
    )

    if job.user_id:
        Broadcast.user(
            user=job.user_id,
            data=payload,
        )