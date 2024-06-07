import uuid
from enum import Enum, unique
from typing import List

from pydantic import BaseModel, Field


@unique
class Lang(str, Enum):
    EN = "en"
    ZH = "zh"


class DocIndex(BaseModel):
    doc_id: str


class Roadmap(BaseModel):
    doc_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    roadmap_qa_text: str
    roadmap_summary_text: str
    summary: str
    title: str
    questions: List[str]
    steps: List[str]


class Document(BaseModel):
    doc_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    content: str
    header: str
    summary: str
    questions: List[str]
    answers: List[str]
    ground_truth: List[str]

class EvaSample(BaseModel):
    doc_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    question: List[str]
    answer: List[str]
    contexts: List[str]
    ground_truth: List[str]
