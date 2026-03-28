from openenv import Task


class TaskDrafting(Task):
    def __init__(self):
        super().__init__(
            id="emailassist_drafting",
            description="Draft professional replies to all threads that require action.",
            difficulty="hard",
        )
