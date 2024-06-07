import json
from enum import Enum, unique
from typing import Dict, Generator, List

import click
import requests


try:
    import platform

    if platform.system() != "Windows":
        import readline  # noqa: F401
except ImportError:
    print("Install `readline` for a better experience.")


@unique
class Action(str, Enum):
    EXIT = "exit"
    SENIOR = "senior"
    ROADMAP = "roadmap"
    ASSIST = "assist"
    CLASSMATE = "classmate"


def get_response(url: str, mentor_id: str, messages: List[Dict[str, str]]) -> List[str]:
    headers = {"Content-Type": "application/json"}
    payload = {"user_id": "0", "mentor_id": mentor_id, "lang": "en", "step": 1, "messages": messages}
    response = requests.post(url, headers=headers, json=payload)
    data = json.loads(response.text)
    return data["roadmap"]


def get_stream_response(
    url: str, mentor_id: str, messages: List[Dict[str, str]], lang: str
) -> Generator[str, None, None]:
    headers = {"Content-Type": "application/json"}
    payload = {"user_id": "0", "mentor_id": mentor_id, "lang": lang, "step": 1, "messages": messages}
    response = requests.post(url, headers=headers, json=payload, stream=True)
    for line in response.iter_lines(decode_unicode=True):
        if line and str(line).startswith("data:"):
            data = json.loads(line[6:])
            if data.get("content", None) is not None:
                yield data["content"]
            else:
                break


if __name__ == "__main__":
    base_url = "http://localhost:9000/v1"

    mentor_id = click.prompt("Mentor name", type=str)
    lang = click.prompt("Lang", type=str)

    while True:
        action = click.prompt("Action", type=click.Choice([act.value for act in Action]))
        if action == Action.EXIT:
            break

        query = click.prompt("User", type=str)
        messages = [{"role": "user", "content": query}]

        if action == Action.ROADMAP:
            print("Roadmap:")
            for step in get_response(base_url + "/plato/roadmap", mentor_id, messages):
                print(step)

        elif action == Action.SENIOR:
            print("Senior Plato: ", end="", flush=True)
            for new_text in get_stream_response(base_url + "/plato/senior", mentor_id, messages, lang):
                print(new_text, end="", flush=True)
            print()

        elif action == Action.ASSIST:
            print("Assistant Plato: ", end="", flush=True)
            for new_text in get_stream_response(base_url + "/plato/assistant", mentor_id, messages, lang):
                print(new_text, end="", flush=True)
            print()

        elif action == Action.CLASSMATE:
            print("Classmate Plato: ", end="", flush=True)
            for new_text in get_stream_response(base_url + "/plato/classmate", mentor_id, messages, lang):
                print(new_text, end="", flush=True)
            print()
