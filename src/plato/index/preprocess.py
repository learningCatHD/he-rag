#using utf-8
import os
import hashlib
import json
import pickle
import traceback
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union
from openai import OpenAI
from collections import OrderedDict

from tqdm import tqdm
from .parser import clean_markdown_text 
from ..common.types import DocIndex, Document, Roadmap
from plato.utils import Convert
from ..common.types import Lang
import traceback
from plato.index.extract import Extractor


class PreProcess:
    def __init__(self, model_name: str, base_url: str="", api_key="0", language="Chinese") -> None:
        self.extractor =  Extractor(model_name=model_name,
                                    base_url=base_url,
                                    api_key=api_key,
                                    language=language
                                    )
    
    def _extract_item(self, data: Dict[str, Any], filename:str, output:Path) -> "Document":
        try:
            roadmap_dir = output / "roadmap"
            if not roadmap_dir.exists():
                roadmap_dir.mkdir()
            document_dir = output / "document"
            if not document_dir.exists():
                document_dir.mkdir()
            
            roadmap_quests = []
            questions = self.extractor._generate_question(data["content"])
            summary = self.extractor._extract_summary(data["content"])
            
            roadmap_quests.extend(questions)           
            sub_file = filename.split('.json')[0]
            content_data = {
                'header': sub_file,
                'body': data["content"],
                'questions': questions,
                'summary':summary 
            }

            document_file_path = document_dir / "{}.json".format(sub_file)
            with open(document_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(content_data, json_file, ensure_ascii=False, indent=4)
                
            document = Document(header=content_data['header'],
                                body=content_data['body'],
                                summary=content_data['summary'],
                                questions=content_data['questions']
                                )
        except Exception as e:
            traceback.print_stack()
            if isinstance(e,json.JSONDecodeError):
                print(f"Error decoding JSON from file {filename}")
        return document  

            # roadmap_summary = self._generate_roadmap_summary(topics=topics)
            # article_summary = self._generate_article_summary(article=data)
            
            # roadmap_file = "roadmap&" + filename.split('.json')[0] 
            # roadmap_data = {
            #     'title': roadmap_file,
            #     'roadmap_summary': roadmap_summary,
            #     'summary': article_summary,
            #     'topics': topics,
            #     'steps': roadmap_quests
            # }
            # document_file_path = roadmap_dir / "{}.json".format(roadmap_file)
            # with open(document_file_path, 'w', encoding='utf-8') as json_file:
            #     json.dump(roadmap_data, json_file, ensure_ascii=False, indent=4)                        
            
             

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
    def _dump_cache(dump_path: Path, processed_items: Dict[str, Union["Document", "Roadmap"]]) -> None:
        item_list = []
        for item in processed_items.values():
            item_list.append(item.model_dump(exclude_unset=True))

        with open(dump_path, "w", encoding="utf-8") as dump_file:
            json.dump(item_list, dump_file, indent=2, ensure_ascii=False)
   
    def run(self, folder: Path, output: Path) -> None:
        input_files: List[Path] = []
        for path in folder.rglob("*.*"):
            if path.is_file() and path.suffix == ".json":
                input_files.append(path)

        processed_items, new_items = {}, {}
        cache_path = folder.parent / "{}.pkl".format(folder.name)
        dump_path = folder.parent / "{}.json".format(folder.name)
        if cache_path.is_file():
            self._load_cache(cache_path, processed_items)
            print("Loaded {} items.".format(len(processed_items)))

        for i, file_path in enumerate(tqdm(input_files, desc="Build index")):
            with open(file_path, "rb") as binary_file:
                file_hash = hashlib.sha1(binary_file.read()).hexdigest()

            try:
                if file_hash not in processed_items:
                    with open(file_path, "r", encoding="utf-8") as input_file:
                        new_items[file_hash] = self._extract_item(json.load(input_file), file_path.name, output)

                if (i + 1) % 10 == 0 and len(new_items):
                    self._save_cache(cache_path, processed_items, new_items)
            except KeyboardInterrupt:
                print("Aborted!")
                break
            except Exception:
                traceback.print_exc()
                new_items[file_hash] = -1

        if len(new_items):
            self._save_cache(cache_path, processed_items, new_items)

        self._dump_cache(dump_path, processed_items)
        print("Successfully built {} items.".format(len(processed_items)))
