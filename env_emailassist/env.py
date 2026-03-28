import random
from typing import Optional, List, Dict
from datetime import datetime
from openenv import OpenEnv, Episode, Task, ActionResult

from .models import (
    EmailMessage,
    EmailThread,
    Observation,
    Action,
    Reward,
    State
)


# ---------------------------------------------------------
# Utility: create deterministic timestamps
# ---------------------------------------------------------

def make_ts(i: int) -> str:
    return datetime(2025, 1, 15, 9 + i, 30).isoformat()


# ---------------------------------------------------------
# Hardcoded realistic-neutral inbox with 8 threads
# ---------------------------------------------------------

def generate_default_inbox() -> List[EmailThread]:

    return [
        EmailThread(
            thread_id="T1",
            subject="Project Timeline Clarification",
            participants=["Alex Morgan", "You"],
            importance=0.9,
            urgency="high",
            requires_action=True,
            expected_reply_keywords=["timeline", "update", "schedule"],
            messages=[
                EmailMessage(
                    sender="Alex Morgan",
                    timestamp=make_ts(0),
                    content=(
                        "Hi, could you send an updated project timeline? "
                        "The client wants to review it by tomorrow."
                    ),
                    is_reply=False
                )
            ]
        ),

        EmailThread(
            thread_id="T2",
            subject="Weekly Team Meeting Notes",
            participants=["Jordan Kim", "You"],
            importance=0.4,
            urgency="low",
            requires_action=False,
            expected_reply_keywords=[],
            messages=[
                EmailMessage(
                    sender="Jordan Kim",
                    timestamp=make_ts(1),
                    content="Here are the meeting notes from today's sync. No action needed.",
                    is_reply=False
                )
            ]
        ),

        EmailThread(
            thread_id="T3",
            subject="Invoice Follow-up",
            participants=["Taylor Brooks", "You"],
            importance=0.8,
            urgency="medium",
            requires_action=True,
            expected_reply_keywords=["invoice", "payment", "confirm"],
            messages=[
                EmailMessage(
                    sender="Taylor Brooks",
                    timestamp=make_ts(2),
                    content=(
                        "Just checking in regarding the pending invoice. "
                        "Could you confirm if it has been processed?"
                    ),
                    is_reply=False
                )
            ]
        ),

        EmailThread(
            thread_id="T4",
            subject="Team Lunch Plan",
            participants=["Jamie Lee", "You"],
            importance=0.2,
            urgency="low",
            requires_action=False,
            expected_reply_keywords=[],
            messages=[
                EmailMessage(
                    sender="Jamie Lee",
                    timestamp=make_ts(3),
                    content="We're planning a team lunch this Friday. Let me know if you're joining!",
                    is_reply=False
                )
            ]
        ),

        EmailThread(
            thread_id="T5",
            subject="System Access Request",
            participants=["Support Desk", "You"],
            importance=0.7,
            urgency="medium",
            requires_action=True,
            expected_reply_keywords=["access", "request", "approve"],
            messages=[
                EmailMessage(
                    sender="Support Desk",
                    timestamp=make_ts(4),
                    content="Please approve the new system access request for the onboarding user.",
                    is_reply=False
                )
            ]
        ),

        EmailThread(
            thread_id="T6",
            subject="Reminder: Compliance Form",
            participants=["HR Department", "You"],
            importance=0.6,
            urgency="medium",
            requires_action=False,
            expected_reply_keywords=[],
            messages=[
                EmailMessage(
                    sender="HR Department",
                    timestamp=make_ts(5),
                    content="Reminder to complete the compliance form by end of week.",
                    is_reply=False
                )
            ]
        ),

        EmailThread(
            thread_id="T7",
            subject="Client Document Revision",
            participants=["Client Support", "You"],
            importance=0.85,
            urgency="high",
            requires_action=True,
            expected_reply_keywords=["document", "revision", "update"],
            messages=[
                EmailMessage(
                    sender="Client Support",
                    timestamp=make_ts(6),
                    content=(
                        "The client requested a revision to the document. "
                        "Can you provide the updated version?"
                    ),
                    is_reply=False
                )
            ]
        ),

        EmailThread(
            thread_id="T8",
            subject="Promotional Offer",
            participants=["Marketing Mailer"],
            importance=0.1,
            urgency="low",
            requires_action=False,
            expected_reply_keywords=[],
            messages=[
                EmailMessage(
                    sender="Marketing Mailer",
                    timestamp=make_ts(7),
                    content="Don't miss our new promotional offer! Limited time only.",
                    is_reply=False
                )
            ]
        )
    ]


# ---------------------------------------------------------
# EmailAssist Environment
# ---------------------------------------------------------

class EmailAssistEnv(OpenEnv):

    def __init__(self):
        super().__init__()
        self.max_steps = 30
        self.reset()

    # ------------------------------------------------------
    # Reset environment per task
    # ------------------------------------------------------
    def reset(self, task: Optional[Task] = None) -> Episode:
        self.task = task or Task(id="emailassist_classify")

        self.inbox = generate_default_inbox()
        self.opened_thread_id = None
        self.step_count = 0
        self.history = []

        return Episode(observation=self._get_observation())

    # ------------------------------------------------------
    # Process actions
    # ------------------------------------------------------
    def step(self, action: Action) -> ActionResult:
        self.step_count += 1
        reward = 0.0
        done = False

        act = action.action_str.strip()
        self.history.append(act)

        try:
            if act.startswith("open_thread"):
                tid = act.split("(")[1].split(")")[0]
                if any(t.thread_id == tid for t in self.inbox):
                    self.opened_thread_id = tid
                else:
                    reward -= 0.05

            elif act.startswith("classify"):
                if self.task.id == "emailassist_classify":
                    tid, label = self._parse_two(act)
                    reward += self._grade_classification(tid, label)

            elif act.startswith("set_priority"):
                if self.task.id == "emailassist_priority":
                    tid, val = self._parse_two(act)
                    reward += self._grade_priority(tid, val)

            elif act.startswith("draft_reply"):
                if self.task.id == "emailassist_drafting":
                    tid, text = self._parse_two(act)
                    reward += self._grade_reply(tid, text)

            elif act.startswith("delete"):
                tid = act.split("(")[1].split(")")[0]
                self.inbox = [t for t in self.inbox if t.thread_id != tid]

        except:
            reward -= 0.1  # invalid action format

        # Base step penalty to prevent infinite loops
        reward -= 0.005

        if self.step_count >= self.max_steps:
            done = True

        return ActionResult(
            observation=self._get_observation(),
            reward=Reward(reward=reward),
            done=done,
        )

    # ------------------------------------------------------
    # Observation builder
    # ------------------------------------------------------
    def _get_observation(self) -> Observation:
        inbox_summary = [
            {
                "thread_id": t.thread_id,
                "subject": t.subject,
                "importance": t.importance,
                "urgency": t.urgency,
                "requires_action": t.requires_action,
            }
            for t in self.inbox
        ]

        opened = None
        if self.opened_thread_id:
            opened = next(t for t in self.inbox if t.thread_id == self.opened_thread_id)

        return Observation(
            inbox_summary=inbox_summary,
            opened_thread=opened,
            goal=self.task.description,
            steps_left=self.max_steps - self.step_count,
            history=self.history[-5:],  # last 5 actions
        )

    # ------------------------------------------------------
    # Parsing helper
    # ------------------------------------------------------
    def _parse_two(self, action_str: str):
        inner = action_str[action_str.find("(")+1 : action_str.rfind(")")]
        a, b = inner.split(",", 1)
        return a.strip(), b.strip()

    # ------------------------------------------------------
    # Graders (simple deterministic versions)
    # ------------------------------------------------------

    def _grade_classification(self, tid: str, label: str) -> float:
        labels = {
            "T1": "Work",
            "T2": "Info",
            "T3": "ClientRequest",
            "T4": "Personal",
            "T5": "Work",
            "T6": "Info",
            "T7": "ClientRequest",
            "T8": "Spam"
        }
        if tid not in labels:
            return -0.05
        return 0.05 if label == labels[tid] else -0.05

    def _grade_priority(self, tid: str, val: str) -> float:
        ideal = {
            "T1": 5,
            "T3": 4,
            "T7": 5,
            "T5": 4,
            "T6": 3,
            "T2": 2,
            "T4": 1,
            "T8": 1
        }
        try:
            val = int(val)
            if tid not in ideal:
                return -0.05
            diff = abs(val - ideal[tid])
            if diff == 0:
                return 0.1
            elif diff == 1:
                return 0.05
            else:
                return -0.1
        except:
            return -0.1

    def _grade_reply(self, tid: str, text: str) -> float:
        thread = next((t for t in self.inbox if t.thread_id == tid), None)
        if not thread:
            return -0.1

        if not thread.requires_action:
            return -0.05

        reward = 0.0

        # Keyword checks
        for kw in thread.expected_reply_keywords:
            if kw.lower() in text.lower():
                reward += 0.05

        # Tone check
        polite_words = ["thank", "please", "let me know", "regards"]
        if any(w in text.lower() for w in polite_words):
            reward += 0.05

        # Structure check
        if len(text.split()) > 5:
            reward += 0.05

        return reward
