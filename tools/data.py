import argparse
import json
from pathlib import Path
from typing import List, Dict, Union
from tqdm import tqdm
import pandas as pd

def _transfer_to_hipporag_corpus(file_path:Path, data:List[Dict]):
    odata = []
    for i, item in enumerate(tqdm(data, desc="transfer hipporag")):
        _item = {}
        _item['title'] = item['header']
        _item['text'] = item['content'][0]
        _item['idx'] = i
        odata.append(_item)
    ofile = 'hipporag_corpus.json'
    opath = file_path.parent.parent / "{}".format(ofile)
    with open(opath, "w", encoding="utf-8") as dump_file:
        json.dump(odata, dump_file, indent=2, ensure_ascii=False)       
    return

def _transfer_to_hipporag(file_path:Path, data:List[Dict]):
    odata = []
    for _, item in enumerate(tqdm(data, desc="transfer hipporag")):
        for i in range(len(item['questions'])):
            _item = {}
            _item["id"] = file_path.name
            _item['question'] = item['questions'][i]
            _item['answer'] = [item['ground_truth'][i]]
            _item['answerable'] = True
            _item['paragraphs'] = [{
                "title": item["header"],
                "text": item["content"],
                "is_supporting": True,
                "idx": 0
            }]
            odata.append(_item)
    ofile = 'hipporag.json'
    opath = file_path.parent.parent / "{}".format(ofile)
    with open(opath, "w", encoding="utf-8") as dump_file:
        json.dump(odata, dump_file, indent=2, ensure_ascii=False)       
    return

def _transfer_to_selfrag(file_path:Path, data:List[Dict]):
    odata = []
    for i, item in enumerate(tqdm(data, desc="transfer selfrag")):
        _item = {}
        _item["id"] = str(i)
        _item['text'] = '\n'.join(item['content'])
        _item['title'] = item['header']
        odata.append(_item)
    df = pd.DataFrame(odata)
    ofile = 'transfer_to_selfrag.tsv'
    opath = file_path.parent.parent / "{}".format(ofile)
    df.to_csv(opath, index=False, sep="\t")
    return


def _extract_query(file_path:Path, data:List[Dict]):
    questions = []
    for item in tqdm(data):
        questions.extend(item["questions"])
    odata = {}
    odata["questions"] = questions
    ofile = 'query.jsonl'
    opath = file_path.parent.parent / "{}".format(ofile)
    with open(opath, "w", encoding="utf-8") as dump_file:
        # lines = [line + '\n' for line in odata]
        # dump_file.writelines(lines)
        json.dump(odata, dump_file, indent=2, ensure_ascii=False)           
    return

class Transfer:
    
    def _save(self, file:Path, data: Union[List[Dict], List])-> None:
        if isinstance(data[0], Dict):
            with open(file, "w", encoding="utf-8") as dump_file:
                json.dump(data, dump_file, indent=2, ensure_ascii=False)
        else:
            with open(file, "w", encoding="utf-8") as dump_file:
                lines = [line + '\n' for line in data]
                dump_file.writelines(lines)
    
    def run(self, folder: Path, data_func) -> None:
        input_files: List[Path] = []
        for path in folder.rglob("*.*"):
            if path.is_file() and path.suffix == ".json":
                input_files.append(path)

        for _, file_path in enumerate(tqdm(input_files, desc='data transfer')):
            with open(file_path, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
                data_func(file_path, data)


def main(args):
    transfer = Transfer()
    if args.type == 'hipporag':
        transfer.run(Path(args.folder), _transfer_to_hipporag_corpus)
        transfer.run(Path(args.folder), _transfer_to_hipporag)
    elif args.type == 'selfrag':
        transfer.run(Path(args.folder), _transfer_to_selfrag)
        transfer.run(Path(args.folder), _extract_query)
    elif args.type == 'all':
        transfer.run(Path(args.folder), _transfer_to_hipporag)
        transfer.run(Path(args.folder), _transfer_to_selfrag)
        transfer.run(Path(args.folder), _extract_query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="directory with .json file containing source data",
    )
    parser.add_argument("--type", type=str, default=None, help="file")

    args = parser.parse_args()
    main(args)