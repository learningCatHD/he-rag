from cardinal import Function, Template


QUESTION_FUNCTION = Function(
    name="question_extraction",
    desp="Generate hypothetical questions from the given text",
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

QUESTION_TEMPLATE = Template(
    "Generate a list of 3 hypothetical questions "
    "that could be addressed using the information in the given text. "
    "Ensure each question explores a different angle or aspect of the subject matter. "
    "Start from easier questions and gradually escalate in difficulty. \n\n{text}"
)

SUMMARY_TEMPLATE = Template(
    "Write a concise and precise summary of the following document in a few sentences, "
    "emphasizing the key arguments or findings. \n\n{text}"
)
