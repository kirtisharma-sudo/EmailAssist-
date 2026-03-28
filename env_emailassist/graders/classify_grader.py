from openenv import Grader


class ClassifyGrader(Grader):
    def __init__(self):
        super().__init__(id="grader_classify")

    def grade(self, episode):
        # Environment handles scoring; here we pass final reward sum.
        return episode.total_reward
