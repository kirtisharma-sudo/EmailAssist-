from openenv import Grader


class PriorityGrader(Grader):
    def __init__(self):
        super().__init__(id="grader_priority")

    def grade(self, episode):
        return episode.total_reward
