#using utf-8
import hashlib
import json
import pickle
import traceback
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union

from tqdm import tqdm
from plato.index.parser import clean_markdown_text 
from plato.common import Document, Roadmap
from plato.utils import Convert
from .extract import Extractor
from collections import deque

class Generator:
    def __init__(self, model_name: str, base_url: str="", api_key="0") -> None:
        self.extractor =  Extractor(model_name=model_name,
                                    base_url=base_url,
                                    api_key=api_key,
                                    )
    
    def _extract_item(self, data: str) -> List[Document]:
        try:
            c_data = Convert().md_to_dict(clean_markdown_text(data))
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
                    content = '\n'.join(origin_content)
                    if len(content) < 100:
                        continue
                                        
                    questions = self.extractor._generate_question(content)
                    answers = []
                    for question in questions:
                        answers.append(self.extractor._gen_answer(content, question))
                                            
                    summary = self.extractor._generate_summary(content)
                    level, header = key.split('_', 1) if '_' in key else (key, '')
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
        except Exception as e:
            traceback.print_exc()
            print(f"Exception happened: {str(e)}")
            
        return documents

    @staticmethod
    def _load_cache(cache_path: Path, processed_items: Dict[str, Union["Document", "Roadmap"]]) -> None:
        with open(cache_path, "rb") as cache_file:
            processed_items.update(pickle.load(cache_file))

    @staticmethod
    def _save_cache(
        cache_path: Path,
        processed_items: Dict[str, Union["Document", "Roadmap"]],
        new_items: Dict[str, Union["Document", "Roadmap"]],
    ) -> None:
        with open(cache_path, "wb") as cache_file:
            processed_items.update(new_items)
            pickle.dump(processed_items, cache_file)
              
        
    @staticmethod
    def _dump_data(dump_path: Path, sample_path: Path, processed_items: Dict[str, List[Document]]) -> None:
        item_list = []
        sample_list = []
        for key, item in processed_items.items():
            if not item or item == -1:
                print(key, " does not have a right value")
            else:
                for m in item:
                    if not m:
                        continue
                    item_list.append(m.model_dump(exclude_unset=True))                
                    eval_item = {}
                    length = min(len(m.questions), len(m.answers))
                    eval_item['question'] = m.questions[0:length]
                    eval_item['answer'] = m.answers[0:length]
                    eval_item['contexts'] = m.content*length
                    eval_item['ground_truth'] = m.answers[0:length] 
                    sample_list.append(eval_item)                

        with open(dump_path, "w", encoding="utf-8") as dump_file:
            json.dump(item_list, dump_file, indent=2, ensure_ascii=False)
        
        with open(sample_path, "w", encoding="utf-8") as dump_file:
            json.dump(sample_list, dump_file, indent=2, ensure_ascii=False)
        
    def _get_file_content(self, file_path: Path) -> str:
        if file_path.suffix == ".md":
            with open(file_path, 'r', encoding='utf-8') as md_file:
                data = md_file.read()
            return data
        if file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
            return data["content"] if "content" in data else ""
   
    def _generate_samples(self, folder: Path) -> None:
        input_files: List[Path] = []
        for path in folder.rglob("*.*"):
            if path.is_file() and path.suffix in [".md", ".json"]:
                input_files.append(path)

        processed_items, new_items = {}, {}
        cache_path = folder.parent / "{}.pkl".format(folder.name)
        dump_path = folder.parent / "{}.json".format(folder.name)
        sample_path = folder.parent / "{}.json".format(folder.name + "_eval_samples")
        if cache_path.is_file():
            self._load_cache(cache_path, processed_items)
            print("Loaded {} items.".format(len(processed_items)))

        for i, file_path in enumerate(tqdm(input_files, desc="Build index")):
            with open(file_path, "rb") as binary_file:
                file_hash = hashlib.sha1(binary_file.read()).hexdigest()

            try:
                if file_hash not in processed_items:
                    new_items[file_hash] = self._extract_item(self._get_file_content(file_path))

                if (i + 1) % 2 == 0 and len(new_items):
                    self._save_cache(cache_path, processed_items, new_items)
            except KeyboardInterrupt:
                print("Aborted!")
                break
            except Exception:
                print(f'\n\n {file_path.name} excepted \n')
                traceback.print_exc()
                break
                
        if len(new_items):
            self._save_cache(cache_path, processed_items, new_items)

        self._dump_data(dump_path, sample_path, processed_items)
        print("Successfully built {} items.".format(len(processed_items)))

        
    def run(self, folder: Path, gen_sample=True):
        if gen_sample == True:
            self._generate_samples(folder)
        
        
    
