#using utf-8
import hashlib
import json
import pickle
import traceback
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union
from pprint import pprint

from tqdm import tqdm
from plato.index.parser import clean_markdown_text 
from plato.common import Document, Roadmap
from plato.utils import Convert
from .extract import Extractor

from cardinal import (
    AssistantMessage,
    AutoStorage,
    ChatOpenAI,
    HumanMessage,
    HybridRetriever,
    MsgCollector,
    SystemMessage,
)

from plato.common.types import DocIndex, Document, Lang, EvaSample
from ..templates.evaluate import (
    GENERATE_ANSWER,
    GENERATE_ANSWER_ZH
)

from datasets import Dataset 
from ragas import evaluate
from ragas.metrics import faithfulness, answer_correctness

class Evaluator:
    def __init__(self, model_name: str, mentor_id: str, base_url: str="", api_key="0") -> None:
        self.extractor =  Extractor(model_name=model_name,
                                    base_url=base_url,
                                    api_key=api_key,
                                    )
        self._template = {
            Lang.EN: GENERATE_ANSWER,
            Lang.ZH: GENERATE_ANSWER_ZH,
        }
        self._retriever = HybridRetriever[DocIndex](
            vectorstore_names=[
                "{}_header".format(mentor_id),
                "{}_summary".format(mentor_id),
                "{}_question".format(mentor_id)
            ],
            weights=[0.8, 0.9, 0.9],
        )
        self._storage = AutoStorage[Document](name=mentor_id)
        self._collector = MsgCollector(storage_name=mentor_id)

    @staticmethod
    def _save_cache(
        cache_path: Path,
        processed_items: Dict[str, "Document"],
        new_items: Dict[str, "Document"],
    ) -> None:
        with open(cache_path, "wb") as cache_file:
            processed_items.update(new_items)
            pickle.dump(processed_items, cache_file)
            
        
    @staticmethod
    def _dump_data(sample_path: Path, processed_items: Dict[str, List[EvaSample]]) -> None:
        item_list = []
        sample_list = []
        for key, item in processed_items.items():
            if item == -1:
                print(key, " does not have a right value")
            else:
                for m in item:
                    item_list.append(m.model_dump(exclude_unset=True))                
                    eval_item = {}
                    length = min(len(m.question), len(m.answer))
                    eval_item['question'] = m.question[0:length]
                    eval_item['answer'] = m.answer[0:length]
                    eval_item['contexts'] = m.contexts[0:length]
                    eval_item['ground_truth'] = m.ground_truth[0:length] 
                    sample_list.append(eval_item)                
        
        with open(sample_path, "w", encoding="utf-8") as dump_file:
            json.dump(sample_list, dump_file, indent=2, ensure_ascii=False)

    @staticmethod
    def _load_cache(cache_path: Path, processed_items: Dict[str, Union["Document", "Roadmap"]]) -> None:
        with open(cache_path, "rb") as cache_file:
            processed_items.update(pickle.load(cache_file))
            
    def _retrieve_generate_answer(self, data: List[Dict[str, Dict]]) -> List[EvaSample]:
        try:
            eval_samples = []
            for item in data:
                item["answers"] = []
                contexts = []
                for question in item["questions"]:
                    indexes = self._retriever.retrieve(question, top_k=1)
                    documents = [self._storage.query(index.doc_id) for index in indexes]
                    context = "\n".join(["<doc>{}</doc>".format(document.content) for document in documents if document])
                    contexts.append(context)
                    item["answers"].append(self.extractor._gen_answer(context, question))
                
                length = min(len(item['questions']), len(item['answers']))
                sample = EvaSample(
                    question = item["questions"][:length],
                    answer = item["answers"][:length],
                    contexts = contexts[:length],
                    ground_truth = item["ground_truth"]
                )
                eval_samples.append(sample)
                
        except Exception as e:
            traceback.print_exc()
            print(f"Exception happened: {str(e)}")
            return
        return eval_samples
    
    def _generate_ragas_samples(self, folder:Path) -> None:
        input_files: List[Path] = []
        for path in folder.rglob("*.*"):
            if path.is_file() and path.suffix == ".json":
                input_files.append(path)

        processed_items, new_items = {}, {}
        cache_path = folder.parent / "{}.pkl".format(folder.name)
        sample_path = folder.parent / "eval/{}.json".format(folder.name + "_ragas_samples")
        # if cache_path.is_file():
        #     self._load_cache(cache_path, processed_items)
        #     print("Loaded {} items.".format(len(processed_items)))

        for i, file_path in enumerate(tqdm(input_files, desc="Build index")):
            with open(file_path, "rb") as binary_file:
                file_hash = hashlib.sha1(binary_file.read()).hexdigest()

            try:
                if file_hash not in processed_items:
                    with open(file_path, "r", encoding="utf-8") as input_file:
                        new_items[file_hash] = self._retrieve_generate_answer(json.load(input_file))

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

        self._dump_data(sample_path, processed_items)
        print("Successfully built {} items.".format(len(processed_items)))
        
    def _eval(self, folder:Path):
        input_files: List[Path] = []
        for path in folder.rglob("*.*"):
            if path.is_file() and path.suffix == ".json":
                input_files.append(path)
        for file in input_files:
            data = {"question":[],
                    "answer":[],
                    "contexts":[],
                    "ground_truth":[]
                    }
            with open(file, "r", encoding="utf-8") as input_file:
                _data = json.load(input_file)
                for item in _data:
                    data["question"].extend(item["question"])
                    data["answer"].extend(item["answer"])
                    data["contexts"].extend(item["contexts"])
                    data["ground_truth"].extend(item["ground_truth"])
            data["contexts"] = [[item] for item in data['contexts']]
            dataset = Dataset.from_dict(data)
            score = evaluate(dataset,metrics=[faithfulness,answer_correctness])
            result_path = file.parent / "{}.json".format(file.name + "ragas_result")
            score.to_pandas()
            score.to_pandas().to_csv(result_path, index=False)
            
    def run(self, doc_file: Path, eval_file: Path):
        # self._generate_ragas_samples(doc_file)
        self._eval(eval_file)
            