from enum import Enum, unique
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv


load_dotenv()

from plato import IndexBuilder, Server, view_logs, Generator, Evaluator  # noqa: E402

try:
    import platform

    if platform.system() != "Windows":
        import readline  # noqa: F401
except ImportError:
    print("Install `readline` for a better experience.")


@unique
class Action(str, Enum):
    BUILD = "build"
    LAUNCH = "launch"
    VIEW = "view"
    PREPROCESS = "preprocess"
    EVAL = 'eval'


@click.command()
@click.option("--config", required=True, prompt="Config file")
@click.option("--action", required=True, type=click.Choice([act.value for act in Action]), prompt="Choose an action")
def interactive_cli(config, action):
    with open(config, "r", encoding="utf-8") as config_file:
        config_dict = yaml.safe_load(config_file)

    if action == Action.PREPROCESS:
        for build_args in config_dict["preprocess"]:
            model = build_args["model"]
            base_url = build_args.get("base_url", "")
            for folder_args in build_args["folders"]:
                folder = Path(folder_args["file"])
                content_key = folder_args["content_key"]
                Generator(model, base_url).run(folder, content_key)
    elif action == Action.BUILD:
        for build_args in config_dict["build"]:
            mentor_id = build_args["mentor"]
            for folder_args in build_args["folders"]:
                folder = Path(folder_args["path"])
                IndexBuilder(mentor_id).build_index(folder)
    elif action == Action.LAUNCH:
        mentor_ids = config_dict["launch"]["mentors"]
        Server(mentor_ids).launch()
    elif action == Action.VIEW:
        mentor_ids = config_dict["view"]["mentors"]
        output_dir = Path(config_dict["view"]["output"])
        view_logs(mentor_ids, output_dir)
    elif action == Action.EVAL:
        for build_args in config_dict["eval"]:
            model = build_args["model"]
            base_url = build_args.get("base_url", "")
            for folder_args in build_args["folders"]:
                doc_file = Path(folder_args["doc_file"])
                eval_file = Path(folder_args["eval_file"])
                Evaluator(model, "LLM", base_url).run(doc_file, eval_file)

if __name__ == "__main__":
    interactive_cli()
