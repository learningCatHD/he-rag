import time
from enum import Enum, unique
from typing import List, Optional

from pydantic import BaseModel, Field

from plato.common.types import Lang


@unique
class Role(str, Enum):
    USER = "user"
    MENTOR = "mentor"


class PlatoMessage(BaseModel):
    content: str
    role: Role


class PlatoRequest(BaseModel):
    user_id: str
    mentor_id: str
    lang: Lang = Lang.ZH
    step: int = 0
    messages: List[PlatoMessage]



class MentorList(BaseModel):
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    mentors: List[str]


class PlatoResponse(BaseModel):
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    content: Optional[str] = None


class RoadmapResponse(BaseModel):
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    roadmap: List[str]

class RegisterInfo(BaseModel):
    username: str
    email: str
    gender: str
    career: str
    password: str

class SmsRequest(BaseModel):
    phone: str
class SmsVerify(BaseModel):
    ref: str
    code: str
class LoginInfo(BaseModel):
    username: str
    password: str
class RegisterResponse(BaseModel):
    code:int
    data: dict[str, str]
class RegisterResponseStatus(BaseModel):
    status: dict[str, str]
    data: dict[str, str]
class QueryRequest(BaseModel):
    uid: str

class GeneralResponse(BaseModel):
    messages: str
