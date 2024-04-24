from dataclasses import dataclass, field
from red_utils.core.dataclass_utils import DictMixin


@dataclass
class CeleryTaskBase(DictMixin):
    success: bool = field(default=False)
    task_id: str | None = field(default=None)


@dataclass
class CeleryTask(CeleryTaskBase):
    """Store the results of a Celery task for an HTTP response.

    Params:
        success (bool): Whether queueing task was successful.
        task_id (str): The `rabbitmq` task ID.

    """

    pass
