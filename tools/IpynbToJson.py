import json
import os
from nbconvert import MarkdownExporter
import nbformat

def notebook_to_md(ipynb_file, output_md_file):
    with open(ipynb_file, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    md_exporter = MarkdownExporter()
    md_body, _ = md_exporter.from_notebook_node(notebook)

    with open(output_md_file, 'w', encoding='utf-8') as f:
        f.write(md_body)


def md_to_json(md_filename, json_filename):
    # 读取MD文件内容
    with open(md_filename, 'r', encoding='utf-8') as md_file:
        md_content = md_file.read()
    
    # 构建JSON数据
    json_data = {
        'content': md_content
    }
    
    # 将JSON数据写入到文件中
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


def convert_directory_notebook_to_md(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.ipynb'):
            md_filename = os.path.join(directory, filename)
            md_filename = os.path.splitext(md_filename)[0] + '.md'
            notebook_to_md(filename, md_filename)


def convert_directory_md_to_json(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            md_filename = os.path.join(directory, filename)
            json_filename = os.path.splitext(md_filename)[0] + '.json'
            md_to_json(md_filename, json_filename)


def main():
    directory = os.getcwd()
    convert_directory_notebook_to_md(directory)
    convert_directory_md_to_json(directory)


if __name__ == "__main__":
    main()
