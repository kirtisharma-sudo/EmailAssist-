import random
import re
from typing import List, Optional, Dict

from pydantic import BaseModel

from .models import (
    Observation,
    Action,
    Reward,
    State,
    EmailMessage,
    EmailThread,
)

# ====== Realistic People & Names =======
REAL_SENDERS = [
    "Priya Sharma <priya.hr@company.com>",
    "Ravi Kumar <ravi.sales@company.com>",
    "Amit Verma <amit.tech@company.com>",
    "Client: John Walker <john@walker-consulting.com>",
    "Client: Sarah Milton <sarah@miltonenterprises.com>",
    "System Notification <no-reply@system.com>",
    "Spam: CryptoBot <crypto@scam.ai>",
]

URGENT_SUBJECTS = [
    "Urgent: Need Update",
    "Deadline Approaching",
    "Immediate Response Required",
]

NORMAL_SUBJECTS = [
    "Meeting Follow-Up",
    "Weekly Report",
    "Team Sync Notes",
]

SPAM_SUBJECTS = [
    "WIN 10000 USD!!!",
    "Your Cashback is Ready",
    "Click to Claim Reward",
]


def generate_thread(thread_id: str) -> EmailThread:
    """Creates a realistic email thread with multiple messages."""

    sender = random.choice(REAL_SENDERS)

    # Define subject types
    if "Spam" in sender:
        subject = random.choice(SPAM_SUBJECTS)
        importance = 0.0
        urgency = "low"
        requires_action = False
        expected_keywords = []
    elif "Client" in sender:
        subject = random.choice(URGENT_SUBJECTS + NORMAL_SUBJECTS)
        importance = random.uniform(0.6, 1.0)
        urgency = random.choice(["medium", "high"])
        requires_action = True
        expected_keywords = ["update", "timeline", "details", "confirmation"]
    elif "System" in sender:
        subject = random.choice(NORMAL_SUBJECTS)
        importance = 0.2
        urgency = "low"
        requires_action = False
        expected_keywords = []
    else:
        subject = random.choice(NORMAL_SUBJECTS)
        importance = random.uniform(0.3, 0.7)
        urgency = "medium"
        requires_action = random.choice([True, False])
        expected_keywords = ["noted", "acknowledge", "follow-up"]

    # Message history (1–3 messages)
    messages = []
    msg_count = random.randint(1, 3)

    for i in range(msg_count):
        messages.append(
            EmailMessage(
                sender=sender if i == 0 else "You",
                timestamp=f"2024-12-0{i+1} 10:{20+i}",
                content=(
                    "Hello, could you please provide an update?"
                    if i == 0
                    else "Following up on this."
                    if i == 1
                    else "Thanks, will do."
                ),
                is_reply=bool(i > 0),
            )
        )

    return EmailThread(
        thread_id=thread_id,
        subject=subject,
        messages=messages,
        participants=[sender, "You"],
        importance=importance,
        urgency=urgency,
        requires_action=requires_action,
        expected_reply_keywords=expected_keywords,
    )


# ===============================================================
#                MAIN ENVIRONMENT CLASS
# ===============================================================

class EmailAssistEnv:

    MAX_STEPS = 20

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.step_count = 0
        self.history = []
        self.opened_thread_id = None
        self.inbox: List[EmailThread] = []

    # ---------------- RESET -----------------
    def reset(self) -> Observation:
        self.step_count = 0
        self.history = []
        self.opened_thread_id = None

        # Create inbox of 5-7 threads
        self.inbox = [generate_thread(f"t{i}") for i in range(random.randint(5, 7))]

        goal = self._task_goal()

        return Observation(
            inbox_summary=self._summaries(),
            opened_thread=None,
            goal=goal,
            steps_left=self.MAX_STEPS,
            history=[],
        )

    # ---------------- STATE -----------------
    def state(self) -> State:
        return State(
            inbox=self.inbox,
            opened_thread_id=self.opened_thread_id,
            step_count=self.step_count,
            task_id=self.task_id,
        )

    # ---------------- STEP -----------------
    def step(self, action: Action):
        """Parse and execute the action."""

        self.step_count += 1
        action_str = action.action_str.strip()

        reward_value = 0.0

        # Parse commands
        if action_str.startswith("open_thread"):
            reward_value += self._handle_open_thread(action_str)

        elif action_str.startswith("classify"):
            reward_value += self._handle_classify(action_str)

        elif action_str.startswith("set_priority"):
            reward_value += self._handle_priority(action_str)

        elif action_str.startswith("draft_reply"):
            reward_value += self._handle_reply(action_str)

        elif action_str.startswith("delete"):
            reward_value += self._handle_delete(action_str)

        elif action_str.startswith("flag"):
            reward_value += self._handle_flag(action_str)

        elif action_str.startswith("noop"):
            reward_value += 0.0

        else:
            reward_value -= 0.1  # invalid action penalty

        # Save to history
        self.history.append(action_str)

        done = self._check_done()

        obs = Observation(
            inbox_summary=self._summaries(),
            opened_thread=self._opened_thread(),
            goal=self._task_goal(),
            steps_left=max(self.MAX_STEPS - self.step_count, 0),
            history=self.history[-5:],
        )

        return obs, Reward(reward=reward_value), done, {}

    # ===============================================================
    #               ACTION HANDLERS
    # ===============================================================

    def _handle_open_thread(self, action: str) -> float:
        match = re.match(r"open_thread\((.*?)\)", action)
        if not match:
            return -0.1

        tid = match.group(1).strip().strip('"\'')
        if any(t.thread_id == tid for t in self.inbox):
            self.opened_thread_id = tid
            return +0.01  # exploration reward
        return -0.1

    def _handle_classify(self, action: str) -> float:
        # task 1 only
        if self.task_id != "emailassist_classify":
            return -0.05

        match = re.match(r"classify\((.*?),(.*?)\)", action)
        if not match:
            return -0.1

        tid = match.group(1).strip().strip('"\'')
        label = match.group(2).strip().strip('"\'')
        return self._grade_classification(tid, label)

    def _handle_priority(self, action: str) -> float:
        # task 2 only
        if self.task_id != "emailassist_priority":
            return -0.05

        match = re.match(r"set_priority\((.*?),(.*?)\)", action)
        if not match:
            return -0.1

        tid = match.group(1).strip().strip('"\'')
        try:
            score = int(match.group(2))
        except:
            return -0.1

        return self._grade_priority(tid, score)

    def _handle_reply(self, action: str) -> float:
        # task 3 only
        if self.task_id != "emailassist_drafting":
            return -0.05

        match = re.match(r"draft_reply\((.*?),(.*?)\)", action)
        if not match:
            return -0.1

        tid = match.group(1).strip().strip('"\'')
        text = match.group(2).strip().strip('"\'')
        return self._grade_reply(tid, text)

    def _handle_delete(self, action: str) -> float:
        return -0.02  # minor penalty; risky action

    def _handle_flag(self, action: str) -> float:
        return -0.01  # minor penalty unless spam (TODO extend later)

    # ===============================================================
    #              TASK GOAL TEXT
    # ===============================================================

    def _task_goal(self) -> str:
        goals = {
            "emailassist_classify": "Classify each thread as Work, Personal, ClientRequest, Spam, Info, or Meeting.",
            "emailassist_priority": "Assign priority scores (1–5) to all email threads.",
            "emailassist_drafting": "Draft professional replies for all threads requiring a response.",
        }
        return goals[self.task_id]

    # ===============================================================
    #              GRADING LOGIC
    # ===============================================================

    def _grade_classification(self, tid: str, label: str) -> float:
        thread = next((t for t in self.inbox if t.thread_id == tid), None)
        if not thread:
            return -0.1

        # Rough heuristic labeling:
        if "Spam" in thread.participants[0] or "spam" in thread.subject.lower():
            true_label = "Spam"
        elif "Client" in thread.participants[0]:
            true_label = "ClientRequest"
        elif "Meeting" in thread.subject:
            true_label = "Meeting"
        elif "System" in thread.participants[0]:
            true_label = "Info"
        else:
            true_label = "Work"

        return 0.05 if label.lower() == true_label.lower() else -0.05

    def _grade_priority(self, tid: str, score: int) -> float:
        thread = next((t for t in self.inbox if t.thread_id == tid), None)
        if not thread:
            return -0.1

        # Expected priority:
        expected = round(
            thread.importance * 5 if thread.urgency == "high" else
            thread.importance * 4 if thread.urgency == "medium" else
            thread.importance * 2
        )

        if score == expected:
            return +0.10
        elif abs(score - expected) == 1:
            return +0.05
        else:
            return -0.05

    def _grade_reply(self, tid: str, text: str) -> float:
        thread = next((t for t in self.inbox if t.thread_id == tid), None)
        if not thread:
            return -0.1

        if not thread.requires_action:
            return -0.05

        reward = 0.0

        # Check for keyword inclusion
        for kw in thread.expected_reply_keywords:
            if kw.lower() in text.lower():
                reward += 0.05

        # Check tone
        if any(p in text.lower() for p in ["thank", "regards", "best", "sure"]):
            reward += 0.05

        # Check for hallucinations: if reply mentions not in thread
        for word in text.split():
            if word.lower() in ["random", "unrelated", "fake"]:
                reward -= 0.1

        # Structure reward
        if len(text.split()) >= 5:
            reward += 0.05

        return reward

    # ===============================================================
    #              HELPER FUNCTIONS
    # ===============================================================

    def _summaries(self) -> List[Dict]:
        """Summary list for observations"""
        return [
            {
                "thread_id": t.thread_id,
                "subject": t.subject,
                "from": t.participants[0],
                "requires_action": t.requires_action,
                "urgency": t.urgency,
            }
            for t in self.inbox
        ]

    def _opened_thread(self) -> Optional[EmailThread]:
        if not self.opened_thread_id:
            return None
        return next((t for t in self.inbox if t.thread_id == self.opened_thread_id), None)

    def _check_done(self) -> bool:
        return self.step_count >= self.MAX_STEPS
