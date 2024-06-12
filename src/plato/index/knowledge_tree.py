from typing import List, Dict
from pydantic import BaseModel, Field
from plato.common import Document, Node
from pathlib import Path
import json

# 示例节点信息，按照层序排列
nodes_info = [
    {"node_id": "root", "is_root": True, "name": "root", "parent": None, "document": "root_doc", "level": 1},
    {"node_id": "child1_1", "is_root": False, "name": "child1_1", "parent": "child1", "document": "child1_1_doc", "level": 3},
    {"node_id": "child1", "is_root": False, "name": "child1", "parent": "root", "document": "child1_doc", "level": 2},
    {"node_id": "child2", "is_root": False, "name": "child2", "parent": "root", "document": "child2_doc", "level": 2}
]

class KGTree:
    def __init__(self, node_file_path) -> None:
        self.nodes = self._load(node_file_path)
        
    def _load(folder: Path) -> Dict[str, Dict[str, Node]]:
        input_files: List[Path] = []
        for path in folder.rglob("*.*"):
            if path.is_file() and path.suffix == ".json":
                input_files.append(path)
        
        for input_file in input_files:
            nodes = {} 
            with open(input_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                for item in data:
                    node = Node(
                        node_id=item["node_id"],
                        is_root=item["is_root"],
                        name=item["name"],
                        parent=item["parent"],
                        children=item["children"],
                        document=item["document"],
                        level=item["level"]                       
                    )
                nodes[item["node_id"]] = node
        return nodes

    def _insert(self):
        pass
    
    def _retreive(self, doc:Document) -> List[Document]:
        documents = []
        node = self.nodes[doc["doc_id"]]
        for child in node.children:
            documents.append(self.nodes[child.node_id])
        return documents
        
    def _save(self):
        pass
    
    