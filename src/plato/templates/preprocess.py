from cardinal import Function, Template


EXTRACT_TOPIC_TEMPLATE = Template(
"The given article is about techniques, Your task is to extract five most relevant topic from the given article."
"Your response is an array of sub topics in the format [\"topic\"] with {language}. Make sure do not output anything else."

"article: {article}"
)

EXTRACT_TOPIC_SUMMARY_TEMPLATE = Template(
"Write a roadmap to learn topics {topics}. "
"The summary should be a high-level overview of the article. Express the output in {language}."
)

GENERATE_KNOWLEGE_TEMPLATE = Template(
"Extract knowledge about topic: {topic} from a Computer Science textbook {article}."
"The knowledge starts with a high-level overview of the topic. Then, it presents a few example and describes the solution in natural language. "
"After that, make a judge if the topic is suitable to be explain by code snippets, but do not show your judgment process. one hint to make the judge is according to if the article has snippets. "
"Do not show your judgment result, just use the result for the following process."
"if the judgement is positive, provides 1 code snippets, following the example.  The coding language is Python 3.6. Each snippet has no more than 10 rows. The code should represent a Python function & its call. All the common ML/DS libraries are available.Don't be too verbose."
"if the judgement is negative, do not provide code snippets."
"Interpret the knowledge in {language} , don't mention the article in the output . "
)

EXTRACT_USUAL_SUMMARY_TEMPLATE = Template(
"Write a summary for given article. "
"The summary should be a high-level overview of the article in one sentence."

"article: {article}"
)


GENERATE_QUESTIONS_TEMPLATE = Template(
"Your task is to proposal questions about the main knowledge about the given article. "
"The question should be help to understand the main idea about the knowledge"
"Your response is an array of the proposed questions in the format [\"question\"]"

"'article': {article}"
)


GENERATE_OVERALL_QUESTIONS_TEMPLATE = Template(
"Your task is to proposal 'two' overall questions from the given hierachical 'article'. "
"The question should be help to understand the main idea about the knowledge, so do not focus too much about the specific detail"
"Do not mention about the article."
"Your response is an array of the proposed questions in the format [\"question\"] "
"Do not output anything else but questions."


"'article': {article}"
)

GENERATE_OVERALL_QUESTIONS_TEMPLATE_ZH = Template(
"你的任务是根据给定的层级化摘要提出三个问题。" 
"首先,从摘要中找出三个知识点。" 
"然后,根据每个知识点提出一个问题。" 
"你的回答是一个提出的问题数组,格式为 [\"question\"]"

"摘要: {article}"
)


QUESTION_FUNCTION = Function(
    name="question_extraction",
    desp="Generate hypothetical questions from the given text could potentially answer",
    params={
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Hypothetical questions that the given text could potentially answer",
            }
        },
        "required": ["questions"],
    },
)

QUESTION_FUNCTION_ZH = Function(
    name="问题抽取",
    desp="从给定文章中提出问题，使得用文章内容能够回答这些问题",
    params={
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "从给定文章中提出问题，使得用文章内容能够回答这些问题",
            }
        },
        "required": ["questions"],
    },
)

TOPIC_EXTRACT_FUNCTION = Function(
    name="topic_extract_function",
    desp="Extract topics from the given text",
    params={
        "type": "object",
        "properties": {
            "topics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "topics that the given text are focused on",
            }
        },
        "required": ["topics"],
    },
)


SUMMARY_TEMPLATE = Template(
    "Write a concise and precise summary of the following document in one sentences, "
    "\n\n{text}"
)

SUMMARY_TEMPLATE_ZH = Template(
"用几句话简明扼要地总结以下文档," 
"着重说明关键论点或发现。\n\n{text}"
)

TRANSLATE_TEMPLATE = Template(
    "Translate the given text into {language}, Make sure the translation absolutely accurate"
    "Don't translate proper nouns"

    "text: {text}"    
)