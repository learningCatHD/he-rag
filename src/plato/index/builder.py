import hashlib
import json
import pickle
import traceback
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union

from cardinal import AutoStorage, AutoVectorStore, ChatOpenAI, FunctionAvailable, HumanMessage
from tqdm import tqdm

from ..templates.index import QUESTION_FUNCTION, QUESTION_TEMPLATE, SUMMARY_TEMPLATE
from .parser import clean_markdown_text, get_markdown_header
from plato.common.types import DocIndex, Document, Roadmap


class IndexBuilder:
    def __init__(self, mentor_id: str, is_roadmap: bool) -> None:
        self._mentor_id = mentor_id
        self._is_roadmap = is_roadmap
        self._chat_model = ChatOpenAI(model="gpt-3.5-turbo")
        self._question_function = QUESTION_FUNCTION
        self._question_template = QUESTION_TEMPLATE
        self._summary_template = SUMMARY_TEMPLATE

    def _extract_questions(self, text: str) -> List[str]:
        tool_call = self._chat_model.function_call(
            messages=[HumanMessage(content=self._question_template.apply(text=text))],
            tools=[FunctionAvailable(function=self._question_function.apply())],
        )
        return tool_call.arguments.get("questions", [])

    def _extract_summary(self, text: str) -> str:
        return self._chat_model.chat(
            messages=[HumanMessage(content=self._summary_template.apply(text=text))],
        )

    def _get_document(self, data: Dict[str, Any]) -> "Document":
        return  Document(
            content ='\n'.join(data['content']) if isinstance(data['content'], list) else data['content'],
            header=data.get("header", ""),
            summary=data.get("summary", ""),
            questions=data.get("questions", []),
            answers=data.get("answers", []),
            ground_truth=data.get("ground_truth", [])
         )

    def _get_roadmap(self, data: Dict[str, Any]) -> "Roadmap":
        return Roadmap(
            roadmap_qa_text = data.get("roadmap_qa_text", ""),
            roadmap_summary_text = data.get("roadmap_summary_text", ""),
            summary=data.get("summary", ""),
            title=data.get("title", ""),
            questions=data.get("questions", []),
            steps=data.get("steps", "")            
        )

    def _create_index(self, entries: Sequence[Tuple[str, "DocIndex"]], index_name: str) -> None:
        texts, data = zip(*entries)
        AutoVectorStore[DocIndex].create(name=index_name, texts=texts, data=data, drop_old=False)

    def _save_documents(self, documents: Sequence["Document"]) -> None:
        doc_ids, header_index, summary_index, question_index = [], [], [], []
        for document in documents:
            if document.header and document.summary and document.questions and document.doc_id:
                doc_index = DocIndex(doc_id=document.doc_id)
                doc_ids.append(document.doc_id)
                header_index.append((document.header, doc_index))
                summary_index.append((document.summary, doc_index))
                for question in document.questions:
                    question_index.append((question, doc_index))
            else:
                documents.remove(document)
                
        AutoStorage[Document](name=self._mentor_id).insert(doc_ids, documents)                
        print(f"saved document num: {len(summary_index)}")
        self._create_index(header_index, index_name="{}_header".format(self._mentor_id))
        self._create_index(summary_index, index_name="{}_summary".format(self._mentor_id))
        self._create_index(question_index, index_name="{}_question".format(self._mentor_id))


    def _save_roadmaps(self, roadmaps: Sequence["Roadmap"]) -> None:
        doc_ids, summary_index, question_index = [], [], []
        for roadmap in roadmaps:
            if  roadmap.steps and roadmap.summary\
                and roadmap.doc_id and roadmap.steps and roadmap.summary:
                doc_index = DocIndex(doc_id=roadmap.doc_id)
                doc_ids.append(roadmap.doc_id)
                summary_index.append((roadmap.summary, doc_index))
                for step in roadmap.steps:
                    question_index.append((step, doc_index))
            else:
                roadmaps.remove(roadmap)
                
        AutoStorage[Roadmap](name="{}_roadmap".format(self._mentor_id)).insert(doc_ids, roadmaps)
        print(f"saved roadmap num: {len(summary_index)}")
        self._create_index(question_index, index_name="{}_roadmap_questions".format(self._mentor_id))
        self._create_index(summary_index, index_name="{}_roadmap_summary".format(self._mentor_id))

    def _get_item(self, data: Dict[str, Any]) -> Union["Document", "Roadmap"]:
        if self._is_roadmap:
            return self._get_roadmap(data)
        else:
            return self._get_document(data)

    def _save_items(self, items: Sequence[Union["Document", "Roadmap"]]) -> None:
        if self._is_roadmap:
            self._save_roadmaps(items)
        else:
            self._save_documents(items)

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
            try:
                item_list.append(item.model_dump(exclude_unset=True))
            except Exception as e:
                traceback.print_exc()
                
        with open(dump_path, "w", encoding="utf-8") as dump_file:
            json.dump(item_list, dump_file, indent=2, ensure_ascii=False)

    def build_index(self, folder: Path) -> None:
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
                        data = json.load(input_file)
                        new_items[file_hash] = self._get_item(data)

                if (i + 1) % 10 == 0 and len(new_items):
                    self._save_cache(cache_path, processed_items, new_items)
            except KeyboardInterrupt:
                print("Aborted!")
                break
            except Exception:
                print("\n exception file: \n", file_path.name)
                traceback.print_exc()
                new_items[file_hash] = -1

        if len(new_items):
            self._save_cache(cache_path, processed_items, new_items)

        completed_items = [item for item in new_items.values() if item != -1]
        if len(completed_items):
            self._save_items(completed_items)

        self._dump_cache(dump_path, processed_items)
        print("Successfully built {} items.".format(len(processed_items)))
