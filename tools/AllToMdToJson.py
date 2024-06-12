from nbconvert import MarkdownExporter
import nbformat
import shutil
import glob
import json
import os
import re

def remove_jsx_from_mdx(mdx_content):
    # 正则表达式匹配JSX标签的模式
    jsx_pattern = r'<\s*[a-zA-Z][^\s>]*[^>]*>.*?<\s*/\s*[a-zA-Z][^\s>]*\s*>'
    
    # 使用正则表达式替换JSX语法部分为空字符串
    md_content = re.sub(jsx_pattern, '', mdx_content, flags=re.DOTALL)
    
    return md_content

def convert_mdx_to_md(mdx_filename, md_filename):
    # 读取MDX文件内容
    with open(mdx_filename, 'r', encoding='utf-8') as mdx_file:
        mdx_content = mdx_file.read()
    
    # 删除MDX文件中的JSX语法部分
    md_content = remove_jsx_from_mdx(mdx_content)
    
    # 将处理后的内容写入到新的.md文件中
    with open(md_filename, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)



def convert_notebook_to_md(ipynb_file, output_md_file):
    with open(ipynb_file, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    md_exporter = MarkdownExporter()
    try:
        md_body, _ = md_exporter.from_notebook_node(notebook)
    except Exception as e:
        print(f"Exception caught: {e}")
        print(f"Filename: '{ipynb_file}'")
        return

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


def convert_md_to_json(src, dst):
    # 创建输出目录
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            convert_md_to_json(s, d)
        elif s.endswith(".md"):
            filename, extension = os.path.splitext(os.path.basename(d))
            new_filename = filename + ".json"
            new_path = os.path.join(os.path.dirname(d), new_filename)
            md_to_json(s, new_path)


def convert_files_to_md(src, dst):
    # 创建输出目录
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            convert_files_to_md(s, d)
        else:
            filename, extension = os.path.splitext(os.path.basename(d))
            new_filename = filename + ".md"
            new_path = os.path.join(os.path.dirname(d), new_filename)
            if s.endswith(".md"):
                shutil.copy(s, new_path)
            elif s.endswith(".mdx"):
                convert_mdx_to_md(s, new_path)
            elif s.endswith('.ipynb'):
                convert_notebook_to_md(s, new_path)


def main():
    input_directory = os.getcwd()
    output_directory = input_directory + "_output"
    convert_files_to_md(input_directory, output_directory)
    convert_md_to_json(output_directory, output_directory)


if __name__ == "__main__":
    print("STARTED!!!")
    main()
    print("DONE!!!")
