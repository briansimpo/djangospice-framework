from dataclasses import dataclass
from typing import Any

from djangospice_framework.core.serializable import Serializable


@dataclass(slots=True, frozen=True)
class JobResult(Serializable):
    """
    Guarantees a uniform return interface for every background job execution.
    """
    result: Any