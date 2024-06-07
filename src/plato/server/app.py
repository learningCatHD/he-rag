import json
from typing import Dict, Generator, List, Sequence, Tuple

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from plato.server.session import UserProfile

from ..mentor import AssistantMentor, ClassmateMentor, RoadmapMentor, SeniorMentor
from .protocol import (
    MentorList,
    PlatoRequest,
    PlatoResponse,
    RoadmapResponse,
    RegisterInfo,
    RegisterResponse,
    QueryRequest,
    GeneralResponse,
    Role,
)


class Server:
    def __init__(self, mentor_ids: Sequence[str]) -> None:
        self.app = FastAPI()
        self.user_profile = UserProfile()
        self.app.add_middleware(
            CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
        )
        self._mentor_ids = mentor_ids
        self._roadmap_mentors = {mentor_id: RoadmapMentor(mentor_id) for mentor_id in mentor_ids}
        self._senior_mentors = {mentor_id: SeniorMentor(mentor_id) for mentor_id in mentor_ids}
        self._assistant_mentors = {mentor_id: AssistantMentor(mentor_id) for mentor_id in mentor_ids}
        self._classmate_mentors = {mentor_id: ClassmateMentor(mentor_id) for mentor_id in mentor_ids}

    def _process_request(self, request: "PlatoRequest") -> List[Tuple[str, str]]:
        if request.mentor_id not in self._mentor_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found.")

        if len(request.messages) % 2 == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid length.")

        for i, message in enumerate(request.messages):
            if i % 2 == 0 and message.role != Role.USER:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role.")
            elif i % 2 == 1 and message.role != Role.MENTOR:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role.")

        return [(message.role.value, message.content) for message in request.messages]

    @staticmethod
    def _ask_mentor(
        mentors: Dict[str, "SeniorMentor"], messages: Sequence[Tuple[str, str]], request: "PlatoRequest"
    ) -> Generator[str, None, None]:
        for content in mentors[request.mentor_id](messages=messages, lang=request.lang, step=request.step):
            yield json.dumps(PlatoResponse(content=content).model_dump(exclude_unset=True), ensure_ascii=False)

        yield json.dumps(PlatoResponse().model_dump(exclude_unset=True), ensure_ascii=False)

    def _register(self, request: "RegisterInfo") -> Tuple[str, str]: 
        uid, response = self.user_profile._register(username=request.username,
                               email=request.email,
                               gender=request.gender,
                               career=request.career,
                               password=request.password
                               )
        return uid, response

    def _user_query(self, request: "QueryRequest") -> str:        
        response = self.user_profile._query(uid=request.uid)
        return response
    
    def _unregister(self, request: "QueryRequest") -> str:        
        response = self.user_profile._unregister(uid=request.uid)
        return response


    def launch(self):
        @self.app.get("/v1/plato/mentors", response_model=MentorList, status_code=status.HTTP_200_OK)
        async def list_mentors():
            return MentorList(mentors=self._mentor_ids)
        
        @self.app.post("/v1/plato/register", response_model=RegisterResponse, status_code=status.HTTP_200_OK)
        async def user_register(request: RegisterInfo):
            user_id, response = self._register(request)
            return RegisterResponse(user_id=user_id, messages=response)

        @self.app.post("/v1/plato/user_query", response_model=RegisterInfo, status_code=status.HTTP_200_OK)
        async def user_query(request: QueryRequest):
            response = self._register(request)
            return RegisterInfo(messages=response)

        @self.app.post("/v1/plato/unregister", response_model=GeneralResponse, status_code=status.HTTP_200_OK)
        async def user_unregister(request: QueryRequest):
            response = self._register(request)
            return GeneralResponse(messages=response)

        @self.app.post("/v1/plato/roadmap", response_model=RoadmapResponse, status_code=status.HTTP_200_OK)
        async def ask_roadmap(request: PlatoRequest):
            messages = self._process_request(request)
            roadmap = self._roadmap_mentors[request.mentor_id](messages=messages)
            return RoadmapResponse(roadmap=roadmap)

        @self.app.post("/v1/plato/senior", response_model=PlatoResponse, status_code=status.HTTP_200_OK)
        async def ask_senior(request: PlatoRequest):
            messages = self._process_request(request)
            generator = self._ask_mentor(self._senior_mentors, messages, request)
            return EventSourceResponse(generator, media_type="text/event-stream")

        @self.app.post("/v1/plato/assistant", response_model=PlatoResponse, status_code=status.HTTP_200_OK)
        async def ask_assistant(request: PlatoRequest):
            messages = self._process_request(request)
            generator = self._ask_mentor(self._assistant_mentors, messages, request)
            return EventSourceResponse(generator, media_type="text/event-stream")

        @self.app.post("/v1/plato/classmate", response_model=PlatoResponse, status_code=status.HTTP_200_OK)
        async def ask_classmate(request: PlatoRequest):
            messages = self._process_request(request)
            generator = self._ask_mentor(self._classmate_mentors, messages, request)
            return EventSourceResponse(generator, media_type="text/event-stream")

        uvicorn.run(self.app, host="0.0.0.0", port=9000, workers=1)
