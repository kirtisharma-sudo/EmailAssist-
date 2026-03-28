from typing import List, Optional, Dict
from pydantic import BaseModel


class EmailMessage(BaseModel):
    sender: str
    timestamp: str
    content: str
    is_reply: bool


class EmailThread(BaseModel):
    thread_id: str
    subject: str
    messages: List[EmailMessage]
    participants: List[str]
    importance: float
    urgency: str
    requires_action: bool
    expected_reply_keywords: List[str]


class Observation(BaseModel):
    inbox_summary: List[Dict]
    opened_thread: Optional[EmailThread]
    goal: str
    steps_left: int
    history: List[str]


class Action(BaseModel):
    action_str: str


class Reward(BaseModel):
    reward: float


class State(BaseModel):
    inbox: List[EmailThread]
    opened_thread_id: Optional[str]
    step_count: int
    task_id: str
