import json
import time
from pathlib import Path
from typing import Sequence

from cardinal import MsgCollector, get_logger


logger = get_logger(__name__)


def view_logs(mentor_ids: Sequence[str], output_dir: Path) -> None:
    output_dir.mkdir(exist_ok=True)
    for mentor_id in mentor_ids:
        collector = MsgCollector(storage_name=mentor_id)
        histories = [[message.model_dump() for message in messages] for messages in collector.dump()]

        output_path = output_dir / "history-{}-{}.json".format(mentor_id, int(time.time()))

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(histories, f, ensure_ascii=False, indent=2)

    logger.info("History saved at: {}".format(output_path))
