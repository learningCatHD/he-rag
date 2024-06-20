import os
import json
from typing import Any, Dict, List, Sequence, Tuple, Union
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from plato.common import Lang, LanguageDict

from cardinal import ChatOpenAI, FunctionAvailable, HumanMessage
from ..templates.evaluate import SUMMARY_TEMPLATE, GENERATE_QUESTIONS_TEMPLATE, QUESTION_FUNCTION, GENERATE_ANSWER
from ..templates.evaluate import SUMMARY_TEMPLATE_ZH, GENERATE_QUESTIONS_TEMPLATE_ZH, QUESTION_FUNCTION_ZH, GENERATE_ANSWER_ZH, TRANSLATE_TEMPLATE
from plato.utils import Convert
from openie import StanfordOpenIE


class Extractor:
    def __init__(self, model_name: str, base_url: str="", api_key="0") -> None:
        api_key = os.environ.get('OPENAI_API_KEY', "")
        if base_url:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        else:
            self.client = OpenAI(
                api_key=api_key,
            )
            
        self.summary_template = {
            Lang.EN: SUMMARY_TEMPLATE,
            Lang.ZH: SUMMARY_TEMPLATE_ZH
        }

        self.generate_questions_template = {
            Lang.EN: GENERATE_QUESTIONS_TEMPLATE,
            Lang.ZH: GENERATE_QUESTIONS_TEMPLATE_ZH
        }
        
        self.question_function_template = {
            Lang.EN: QUESTION_FUNCTION,
            Lang.ZH: QUESTION_FUNCTION_ZH
        }
        
        self.generate_answer_template = {
            Lang.EN: GENERATE_ANSWER,
            Lang.ZH: GENERATE_ANSWER_ZH
        }
        
        self.model = model_name
        self.base_url = base_url

    def _get_content_language(self, content):
        return Convert().judge_language(content)
        
    def _translate(self, text, language):
        if isinstance(text, str):
            query = TRANSLATE_TEMPLATE.apply(language=LanguageDict[language], text=text)
            result = self.client.chat.completions.create(
                messages=[{"role": "user", "content": query}],
                model=self.model,
                temperature=0.2
            )
            return result.choices[0].message.content
        elif isinstance(text, List):
            response = []
            for item in text:
                response.append(self._translate(item, language))
            return response
        
    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(5))            
    def _generate_summary(self, content):
        summary_template = self.summary_template[self._get_content_language(content)]
        query = summary_template.apply(content=content)
        result = self.client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model=self.model,
            temperature=0.5
        )
        response = result.choices[0].message.content
        return response

    def _generate_header(self, summary):
        with StanfordOpenIE() as client:
            triples = client.annotate(summary)
            header = ''.join(triples[0])
        return header
    
    
    
    def _str_list(self, content):
        corrected_string = content.replace('["', '{"').replace('": ', '": "').replace('？, "', '？", "').replace(']', '"}')
        parsed_dict = json.loads(corrected_string)
        questions_list = list(parsed_dict.items())

        return questions_list

    def _generate_question(self, context):
        generate_question = self.generate_questions_template[Lang.EN]
        client = ChatOpenAI(model="gpt-4o")
        tool_call = client.function_call(
            messages=[HumanMessage(content=generate_question.apply(context=context))],
            tools=[FunctionAvailable(function=QUESTION_FUNCTION.apply())],
        )
        response = tool_call.arguments.get("questions", [])
        if self._get_content_language(response) != Lang.EN:
            response = self._translate(response, Lang.EN)
            
            return response
        
        return response
    
    def _update_knowledge_tree(self, metadata):
        pass
        # 1 traverse the root, leaf, down-stream
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def _gen_answer(self, text: str, question: str) -> str:
        generate_answer = self.generate_answer_template[self._get_content_language(text)]
        query = generate_answer.apply(context=text, question=question)
        result = self.client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model=self.model,
            temperature=0.5
        )
        response = result.choices[0].message.content
        return response