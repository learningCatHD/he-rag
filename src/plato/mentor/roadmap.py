from typing import List, Sequence, Tuple

from cardinal import AutoStorage, DenseRetriever,HybridRetriever

from plato.common.types import DocIndex, Roadmap
from pprint import pprint


class RoadmapMentor:
    def __init__(self, mentor_id: str) -> None:
        self._retriever = HybridRetriever[DocIndex](
            vectorstore_names=[
                "{}_roadmap_questions".format(mentor_id),
                "{}_roadmap_summary".format(mentor_id),
            ],
            weights=[0.9, 0.7],
        )
        self._storage = AutoStorage[Roadmap](name="{}_roadmap".format(mentor_id))

    def __call__(self, messages: Sequence[Tuple[str, str]]) -> List[str]:
        query = messages[-1][-1]
        indexes = self._retriever.retrieve(query, top_k=1)
        roadmap = self._storage.query(indexes[0].doc_id)
        print("retrieved documents:]\n")
        pprint(roadmap.summary)
        pprint(roadmap.steps)
        print("\n\n\n")
        return roadmap.steps
