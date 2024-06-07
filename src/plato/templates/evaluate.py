from cardinal import Function, Template


SUMMARY_TEMPLATE = Template(
"Write a breif summary for given content. The summary should be a high-level overview of the article in one sentence.\n\n"
"<content>{content}</content>"
)

SUMMARY_TEMPLATE_ZH = Template(
"为给定的文章写一个简短的总结，总结应该是一句话的高层次概述。\n\n"
"<content>{content}</content>"   
)

GENERATE_QUESTIONS_TEMPLATE = Template(
"Your task is to proposal three questions about the main knowledge about the given context.\n\n "
"The question should be helpful to understand the main idea about the knowledge."
"The number of the question should just be three."
"Your response is an array of the proposed questions in the format [\"question\"]"

"<context>{context}</context>"
)

GENERATE_QUESTIONS_TEMPLATE_ZH = Template(
"你的任务是就给定上下文中的主要知识提出三个问题。\n\n"
"问题应有助于理解知识的主要思想。"
"问题的数量应该恰好是三个。"
"你的回答应该是按照[\"question\"]格式的问题数组。"

"<context>{context}</context>"
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
                "description": "Hypothetical questions that the given context could potentially answer",
            }
        },
        "required": ["questions"],
    },
)

QUESTION_FUNCTION_ZH = Function(
    name="假设问题",
    desp="从给定文章中提取假设问题，提出的问题应该是能够依靠文章找到答案",
    params={
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "假设问题，提出的问题应该是能够从给定文章中找到答案",
            }
        },
        "required": ["questions"],
    },    
)

GENERATE_ANSWER = Template(
    "Answer the question with the necessary information given by the context \n\n"
    "<context>{context}</context>"
    "<question>{question}</question>"
)

GENERATE_ANSWER_ZH = Template(
    "用上下文提供的必要信息回答问题。"
    "<context>{context}</context>"
    "<question>{question}</question>"  
)

TRANSLATE_TEMPLATE = Template(
    "Translate the given text into {language}, Make sure the translation absolutely accurate"
    "Don't translate proper nouns"

    "text: {text}"    
)