import re


def _remove_images(content: str) -> str:
    pattern = re.compile(r"!\[.*?\]\(.*?\)", re.DOTALL)
    return re.sub(pattern, "", content)


def _remove_urls(content: str) -> str:
    pattern = re.compile(r"\[(.*?)\]\(.*?\)", re.DOTALL)
    return re.sub(pattern, r"\1", content)


def _remove_html_tags(content: str) -> str:
    pattern = re.compile(r"<.*?>", re.DOTALL)
    return re.sub(pattern, "", content)


def clean_markdown_text(content: str) -> str:
    content = _remove_images(content)
    content = _remove_urls(content)
    content = _remove_html_tags(content)
    return content


def get_markdown_header(content: str) -> str:
    lines = content.split("\n")
    for line in lines:
        header_match = re.match(r"^#+\s", line)
        if header_match:
            return str(re.sub(r"#", "", line)).strip()
    return "no header"
