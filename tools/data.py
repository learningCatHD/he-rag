import argparse
import json
from pathlib import Path
from typing import List, Dict, Union
from tqdm import tqdm


def _transfer_to_hipporag(data):
    odata = []
    for _, item in enumerate(tqdm(data, desc="transfer hipporag")):
        _item = {}
        _item['title'] = item['header']
        _item['text'] = item['content']
        odata.append(_item)
    return odata

def _transfer_to_selfrag(data):
    odata = []
    for i, item in enumerate(tqdm(data, desc="transfer selfrag")):
        _item = {}
        _item["id"] = str(i)
        _item["section"] = ""
        _item['title'] = item['header']
        _item['text'] = item['content']
        odata.append(_item)
    return odata

def _extract_query(data):
    odata = []
    for item in tqdm(data):
        odata.extend(item["questions"])      
    return odata

class Transfer:
    def __init__(self) -> None:
        pass
    
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
                odata = data_func(data)
            if len(odata):
                opath = file_path.parent.parent / "{}.json".format(data_func.__name__)
                self._save(opath, odata)
                    

def main(args):
    transfer = Transfer()
    if args.type == 'hipporag':
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