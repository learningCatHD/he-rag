import os
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union
from openai import OpenAI
from collections import OrderedDict

from cardinal import AutoStorage, AutoVectorStore, ChatOpenAI, FunctionAvailable, HumanMessage
from tqdm import tqdm
from .parser import clean_markdown_text
from ..templates.preprocess import EXTRACT_USUAL_SUMMARY_TEMPLATE, GENERATE_QUESTIONS_TEMPLATE, QUESTION_FUNCTION, \
    SUMMARY_TEMPLATE, GENERATE_OVERALL_QUESTIONS_TEMPLATE, \
    TRANSLATE_TEMPLATE    
from plato.utils import Convert
from plato.common.types import Lang


class Extractor:
    def __init__(self, model_name: str, base_url: str="", api_key="0", language="Chinese") -> None:
        api_key = os.environ.get('OPENAI_API_KEY', os.defpath)
        if base_url:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        else:
            self.client = OpenAI(
                api_key=api_key,
            )
        self._chat_model = ChatOpenAI(model=model_name)
        self.model = model_name
        self.base_url=base_url
        self.language = language 
    
    def _translate(self, text):
        if isinstance(text, str):
            query = TRANSLATE_TEMPLATE.apply(language=self.language, text=text)
            result = self.client.chat.completions.create(
                messages=[{"role": "user", "content": query}],
                model=self.model,
                temperature=0.2
            )
            return result.choices[0].message.content
        elif isinstance(text, List):
            response = []
            for item in text:
                response.append(self._translate(item))
            return response
            
    def _generate_article_summary(self, article):
        query = EXTRACT_USUAL_SUMMARY_TEMPLATE.apply(article=article)
        result = self.client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model=self.model,
            temperature=0.5
        )
        response = result.choices[0].message.content
        if Convert().judge_language(response) != self.language:
            response = self._translate(response)
        return response

    def _str_list(self, content):
        corrected_string = content.replace('["', '{"').replace('": ', '": "').replace('？, "', '？", "').replace(']', '"}')
        parsed_dict = json.loads(corrected_string)
        questions_list = list(parsed_dict.items())

        return questions_list

    def _generate_question(self, article):
        if self.model.startswith("gpt"):            
            client = ChatOpenAI(model="gpt-4o")
            tool_call = client.function_call(
                messages=[HumanMessage(content=GENERATE_QUESTIONS_TEMPLATE.apply(article=article))],
                tools=[FunctionAvailable(function=QUESTION_FUNCTION.apply())],
            )
            response = tool_call.arguments.get("questions", [])
        else:
            functions = [QUESTION_FUNCTION.apply()]
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": GENERATE_QUESTIONS_TEMPLATE.apply(article=article)}],
                model=self.model,
                functions=functions
            )
            response = self._str_list(response.choices[0].message.content)
            
        if Convert().judge_language(response) != self.language:
            response = self._translate(response)
            return response
        
    def _generate_overall_question(self, article):
        if self.model.startswith("gpt"): 
            client = ChatOpenAI(model="gpt-4o")
            tool_call = client.function_call(
                messages=[HumanMessage(content=GENERATE_OVERALL_QUESTIONS_TEMPLATE.apply(article=article))],
                tools=[FunctionAvailable(function=QUESTION_FUNCTION.apply())],
            )
            response = tool_call.arguments.get("questions", [])
            if Convert().judge_language(response) != self.language:
                response = self._translate(response)
            return response
        else:
            functions = [QUESTION_FUNCTION.apply()]
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": GENERATE_OVERALL_QUESTIONS_TEMPLATE.apply(article=article)}],
                model=self.model,
                functions=functions
            )
            response = self._str_list(response.choices[0].message.content)
            
        if Convert().judge_language(response) != self.language:
            response = self._translate(response)
            return response

    def _extract_summary(self, text: str) -> str:
        query = SUMMARY_TEMPLATE.apply(text=text)
        result = self.client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model=self.model,
            temperature=0.5
        )
        response = result.choices[0].message.content
        if Convert().judge_language(response) != self.language:
            response = self._translate(response)
        return response
    