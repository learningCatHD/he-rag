import os
os.environ['OPENAI_BASE_URL'] = 'http://localhost:11434/v1'
os.environ['OPENAI_API_KEY'] = 'ollama'
from chat_history import chat_history

from cardinal import (
    AssistantMessage,
    AutoStorage,
    ChatOpenAI,
    HumanMessage,
    HybridRetriever,
    MsgCollector,
    SystemMessage,
)

ch = chat_history()
uid = 'test1'
_chat_model = ChatOpenAI(model="llama3:latest")
#ch.set_history(uid, [])

while True:
    augmented_messages = [SystemMessage(content='You are an AI assistant, answer the following questions')]
    c_his = ch.get_history(uid)
    if len(c_his) < 5 and len(c_his) > 0:
        for hum, ass in c_his :
            augmented_messages.append(hum)
            augmented_messages.append(ass)
    if len(c_his) > 5:
        for hum, ass in c_his[-5:]:
            print(len(c_his[-5:]))
            augmented_messages.append(hum)
            augmented_messages.append(ass)
    qu = input('输入：')
    augmented_messages.append(HumanMessage(content=qu))
    response = ""
    for new_token in _chat_model.chat(augmented_messages):
        print(new_token)
        response += new_token
    print("res:",response)
    c_his.append([HumanMessage(content=qu), AssistantMessage(content=response)])
    print(c_his)
    ch.set_history(uid,c_his)
