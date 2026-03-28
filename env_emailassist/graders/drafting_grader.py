from openenv import Grader


class DraftingGrader(Grader):
    def __init__(self):
        super().__init__(id="grader_drafting")

    def grade(self, episode):
        return episode.total_reward
