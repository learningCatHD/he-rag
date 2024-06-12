from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import uuid
from collections import deque

class Node(BaseModel):
    node_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    is_root: bool
    name: str
    parent: Optional[str]
    children: List[str] = []
    document: str

def build_tree_from_level_order(nodes_info: List[Dict], root_id: str) -> Dict[str, Node]:
    if not nodes_info:
        return {}

    nodes = {}
    parent_map = {}

    for info in nodes_info:
        node = Node(**info)
        nodes[node.node_id] = node
        if node.parent:
            if node.parent not in parent_map:
                parent_map[node.parent] = []
            parent_map[node.parent].append(node.node_id)

    for parent_id, children_ids in parent_map.items():
        if parent_id in nodes:
            nodes[parent_id].children = children_ids

    return nodes

def level_order_traversal(nodes: Dict[str, Node], root_id: str) -> List[str]:
    if root_id not in nodes:
        return []
    
    result = []
    queue = deque([root_id])
    
    while queue:
        node_id = queue.popleft()
        node = nodes[node_id]
        result.append(node.node_id)
        
        for child_id in node.children:
            queue.append(child_id)
    
    return result

# 示例节点信息，按照层序排列
nodes_info = [
    {"node_id": "root", "is_root": True, "name": "root", "parent": None, "document": "root_doc"},
    {"node_id": "child1_1", "is_root": False, "name": "child1_1", "parent": "child1", "document": "child1_1_doc"},
    {"node_id": "child1", "is_root": False, "name": "child1", "parent": "root", "document": "child1_doc"},
    {"node_id": "child2", "is_root": False, "name": "child2", "parent": "root", "document": "child2_doc"}
]

# 构建树
root_id = "root"
tree = build_tree_from_level_order(nodes_info, root_id)

# 层序遍历
traversal_result = level_order_traversal(tree, root_id)
print(traversal_result)
