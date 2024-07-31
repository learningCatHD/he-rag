from ..utils import chat_history

ch = chat_history()

uid = '12321312321'
value = []
value.append([HumanMessage(content="hi"), AssistantMessage(content="hi there")])
ch.set_history(uid,value)
aa = ch.get_history(uid)
print(aa)


value.append([HumanMessage(content="h213213i"), AssistantMessage(content="hi the124124re")])

ch.set_history(uid,value)
aa = ch.get_history(uid)
print(aa)