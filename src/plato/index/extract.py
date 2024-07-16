import os
import json
from typing import Any, Dict, List, Sequence, Tuple, Union
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from plato.common import Lang, LanguageDict

from cardinal import ChatOpenAI, FunctionAvailable, HumanMessage
from ..templates.evaluate import SUMMARY_TEMPLATE, GENERATE_QUESTIONS_TEMPLATE, QUESTION_FUNCTION, GENERATE_ANSWER, HEADER_TEMPLATE
from ..templates.evaluate import SUMMARY_TEMPLATE_ZH, GENERATE_QUESTIONS_TEMPLATE_ZH, QUESTION_FUNCTION_ZH, GENERATE_ANSWER_ZH, TRANSLATE_TEMPLATE, HEADER_TEMPLATE_ZH
from plato.utils import Convert
from openie import StanfordOpenIE
from plato.common import Document
from collections import deque
import traceback

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
        
        self.header_template = {
            Lang.EN: HEADER_TEMPLATE,
            Lang.ZH: HEADER_TEMPLATE_ZH
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
        header_template = self.summary_template[self._get_content_language(summary)]
        query = header_template.apply(content=summary)
        result = self.client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model=self.model,
            temperature=0.5
        )
        response = result.choices[0].message.content
        return response
    
    
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
    
    def _extract_content(self, data: str) -> List[Document]:
        try:
            c_data = Convert().md_to_dict(data)
            if not c_data:
                _data = {
                        'title': '',
                        'content': data,
                }
                c_data['0_'] = _data
            
            documents = []
            node_stack = deque()
            node_stack.append(Document(
                content = [],
                header = "",
                summary = "",
                entities = [],
                questions = [],
                answers = [],
                ground_truth = [],
                parent = "",
                children = []                                                               
            ))
            cur_level = -1
            
            for key, value in c_data.items():
                if key and value["content"]:
                    origin_content = value["content"]
                    content = '\n'.join(origin_content) if isinstance(origin_content, list) else origin_content
                    if len(content) < 100:
                        continue
                    if len(content) < 4000:
                        questions = self._generate_question(content)
                        answers = []
                        for question in questions:
                            answers.append(self._gen_answer(content, question))
                                                
                        summary = self._generate_summary(content)
                        try:
                            level, header = key.split('_', 1) if '_' in key else (key, '')
                        except:
                            level = 0
                            header = ""
                        if not header:
                            header = self._generate_header(summary)
                        level = int(level)
                        
                        if level > cur_level:
                            parent = node_stack[-1]
                            document = Document(
                                content = [content],
                                header = header,
                                summary = summary,
                                entities = [],
                                questions = questions,
                                answers = answers,
                                ground_truth = answers,
                                parent = parent.doc_id,
                                children = []
                            )
                            parent.children.append(document.doc_id)
                            node_stack.append(document)  
                            cur_level = level
                        elif level == cur_level:
                            parent = node_stack[-2]
                            document = Document(
                                content = [content],
                                header = header,
                                summary = summary,
                                entities = [],
                                questions = questions,
                                answers = answers,
                                ground_truth = answers,
                                parent = parent.doc_id,
                                children = []
                            )
                            parent.children.append(document.doc_id)
                        elif level < cur_level:                                                
                            for _ in range(level+1 - cur_level):
                                node_stack.pop()
                            parent = node_stack[-1]
                            document = Document(
                                content = [content],
                                header = header,
                                summary = summary,
                                entities = [],
                                questions = questions,
                                answers = answers,
                                ground_truth = answers,
                                parent = parent.doc_id,
                                children = []
                            )
                            parent.children.append(document.doc_id)
                            node_stack.append(document)  
                            cur_level = level                        
                        documents.append(document)
                    else:
                        contents = Convert().split_document(content, 3000)
                        _level, header = key.split('_', 1) if '_' in key else (key, '')
                        for _, content in enumerate(contents):
                            if len(content) < 100:
                                continue
                            questions = self._generate_question(content)
                            answers = []
                            for question in questions:
                                answers.append(self._gen_answer(content, question))
                                                    
                            summary = self._generate_summary(content)
                            header = self._generate_header(summary)
                            level = int(_level) + 1 
                            
                            if level > cur_level:
                                parent = node_stack[-1]
                                document = Document(
                                    content = [content],
                                    header = header,
                                    summary = summary,
                                    entities = [],
                                    questions = questions,
                                    answers = answers,
                                    ground_truth = answers,
                                    parent = parent.doc_id,
                                    children = []
                                )
                                parent.children.append(document.doc_id)
                                node_stack.append(document)  
                                cur_level = level
                            elif level == cur_level:
                                parent = node_stack[-2]
                                document = Document(
                                    content = [content],
                                    header = header,
                                    summary = summary,
                                    entities = [],
                                    questions = questions,
                                    answers = answers,
                                    ground_truth = answers,
                                    parent = parent.doc_id,
                                    children = []
                                )
                                parent.children.append(document.doc_id)
                            elif level < cur_level:                                                
                                for _ in range(level+1 - cur_level):
                                    node_stack.pop()
                                parent = node_stack[-1]
                                document = Document(
                                    content = [content],
                                    header = header,
                                    summary = summary,
                                    entities = [],
                                    questions = questions,
                                    answers = answers,
                                    ground_truth = answers,
                                    parent = parent.doc_id,
                                    children = []
                                )
                                parent.children.append(document.doc_id)
                                node_stack.append(document)  
                                cur_level = level                        
                            documents.append(document)
                        
        except Exception as e:
            traceback.print_exc()
            print(f"Exception happened: {str(e)}")
            
        return documents
    