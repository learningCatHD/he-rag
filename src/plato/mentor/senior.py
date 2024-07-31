import os


from typing import Generator, Sequence, Tuple

from cardinal import (
    AssistantMessage,
    AutoStorage,
    ChatOpenAI,
    HumanMessage,
    HybridRetriever,
    MsgCollector,
    SystemMessage,
)
from plato.utils.chat_history import chat_history
from plato.common.types import DocIndex, Document, Lang
from ..templates.senior import (
    SENIOR_MENTOR_START_TEMPLATE_EN,
    SENIOR_MENTOR_START_TEMPLATE_ZH,
    SENIOR_MENTOR_TEMPLATE_EN,
    SENIOR_MENTOR_TEMPLATE_ZH,
)
from pprint import pprint

os.environ['OPENAI_BASE_URL'] = 'http://localhost:11433/v1'
os.environ['OPENAI_API_KEY'] = 'ollama'

class SeniorMentor:
    def __init__(self, mentor_id: str) -> None:
        self._window_size = 2
        self._chat_model = ChatOpenAI(model="llama3:latest")
        self._start_template = {
            Lang.EN: SENIOR_MENTOR_START_TEMPLATE_EN,
            Lang.ZH: SENIOR_MENTOR_START_TEMPLATE_ZH,
        }
        self._template = {
            Lang.EN: SENIOR_MENTOR_TEMPLATE_EN,
            Lang.ZH: SENIOR_MENTOR_TEMPLATE_ZH,
        }
        self._retriever = HybridRetriever[DocIndex](
            vectorstore_names=[
                "{}_header".format(mentor_id),
                "{}_summary".format(mentor_id),
                "{}_question".format(mentor_id)
            ],
            weights=[0.6, 0.9, 0.9],
        )
        self.ch = chat_history()
        #self._storage = AutoStorage[Document](name=mentor_id)
        #self._collector = MsgCollector(storage_name=mentor_id)

    def __call__(self, messages: Sequence[Tuple[str, str]], lang: Lang, step: int, user_id: str) -> Generator[str, None, None]:
        '''
        query = messages[-1][-1]
        indexes = self._retriever.retrieve(query, top_k=2)
        documents = [self._storage.query(index.doc_id) for index in indexes]
        for document in documents:
            print("retrieved documents:]\n")
            pprint(document.questions)
            pprint(document.content)
            print("\n\n\n")
        context = "\n".join(["<doc>{}</doc>".format(document.content) for document in documents if document])
        template = self._template[lang] if step != 0 else self._start_template[lang]
        '''
        query = messages[-1][-1]
        augmented_messages = [SystemMessage(content='You are an AI assistant, answer the following questions')]
        c_his = self.ch.get_history(user_id)
        if len(c_his) < 5 and len(c_his) > 0:
            for hum, ass in c_his:
                augmented_messages.append(hum)
                augmented_messages.append(ass)
        if len(c_his) > 5:
            for hum, ass in c_his[-5:]:
                augmented_messages.append(hum)
                augmented_messages.append(ass)
        augmented_messages.append(HumanMessage(content=query))
        response = ""
        for new_token in self._chat_model.stream_chat(augmented_messages):
            yield new_token
            response += new_token
        c_his.append([HumanMessage(content=query), AssistantMessage(content=response)])
        self.ch.set_history(user_id, c_his)


        '''
        for role, content in messages[-self._window_size * 2 - 1 :]:
            if role == "user":
                augmented_messages.append(HumanMessage(content=content))
            elif role == "mentor":
                augmented_messages.append(AssistantMessage(content=content))
            else:
                raise ValueError("Unknown role.")

        response = ""
        for new_token in self._chat_model.stream_chat(augmented_messages):
            yield new_token
            response += new_token

        self._collector.collect(augmented_messages + [AssistantMessage(content=response)])
        '''