from openenv import Task


class TaskPriority(Task):
    def __init__(self):
        super().__init__(
            id="emailassist_priority",
            description="Assign priority scores (1–5) to all email threads.",
            difficulty="medium",
        )
