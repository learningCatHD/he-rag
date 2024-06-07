import re
from pprint import pprint
from collections import OrderedDict
import nltk
from nltk.tokenize import sent_tokenize
from plato.common import Lang

class Convert:
    def __init__(self):
        pass
    
    def md_to_dict(self, md_str:str) -> dict:
        result = OrderedDict()
        current_content = []
        current_level = 0
        current_title = ''
        code_block_flag = False  # Flag to indicate if we're inside a code block

        lines = md_str.split("\n")
        for _, line in enumerate(lines):
            if line.strip().startswith("```"):
                code_block_flag = not code_block_flag  # Toggle code block flag

            if not code_block_flag:
                match = re.match(r"^(#{1,6})\s*(.*?)\s*$", line)
            else:
                match = None
                
            if match:
                level = len(match.group(1))
                title = match.group(2)

                if current_title:
                    key = f"{current_level}_{current_title}" if current_title else str(current_level)
                    result[key] = {
                        'title': current_title,
                        'content': current_content,
                    }
                    current_content = []

                current_level = level
                current_title = title
            else:
                if line.strip():
                    current_content.append(line.strip())

        if current_title:
            key = f"{current_level}_{current_title}" if current_title else str(current_level)
            result[key] = {
                'title': current_title,
                'content': current_content,
            }

        return result
    
    def dict_to_md(self, data, level=0):
        md_lines = []
        for key, value in data.items():
            level, title = key.split('_', 1) if '_' in key else (key, '')
            level = int(level)

            if title:
                md_lines.append('#' * level + ' ' + title)

            content = value['content'] if 'content' in value else ""
            md_lines.extend(content)
            md_lines.append('')  # 添加一个空行分隔不同部分

        # 去除最后一个空行
        if md_lines and md_lines[-1] == '':
            md_lines.pop()
        if md_lines:
            return '\n'.join(md_lines) 
        else:
            return ""

    def judge_language(self, text):
        english_count = 0
        chinese_count = 0
        for char in text:
            if '\u0041' <= char <= '\u005a' or '\u0061' <= char <= '\u007a':
                english_count += 1
            elif '\u4e00' <= char <= '\u9fff':
                chinese_count += 1
        if english_count > chinese_count:
            return Lang.EN
        elif chinese_count > english_count:
            return Lang.ZH
        else:
            return Lang.EN
        
    def split_document(self, document, max_length=500):
        sentences = sent_tokenize(document)

        segments = []
        current_segment = ""

        for sentence in sentences:
            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence + " "
            else:
                segments.append(current_segment.strip())
                current_segment = sentence + " "

        if current_segment:
            segments.append(current_segment.strip())

        return segments


if __name__ == "__main__":

    markdown_text = """
    # 标题 1
    ## 子标题 1.1
    这是一些内容
    ## 子标题 1.2
    ### 子子标题 1.2.1
    这是另一些内容
    # 标题 2
    这也是一些内容
    """

    data = Convert().md_to_dict(markdown_text)
    pprint(data)

    result = Convert().dict_to_md(data)
    print(result)
    
    language = Convert().judge_language(markdown_text)
    print(language)
    
    
# import re

# def remove_links_from_file(file_path):
#     # 读取原始文件内容
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()

#     # 使用正则表达式移除链接
#     url_pattern = r'http[s]?://\S+'
#     modified_content = re.sub(url_pattern, '', content)

#     # 将修改后的内容写回文件
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(modified_content)

# # 替换为您要处理的文件的路径
# file_path = '/path/to/your/document.txt'
# remove_links_from_file(file_path)

    