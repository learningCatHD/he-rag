import os
import json

def list_subdirectories(directory):
    subdirectories = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
            subdirectories.extend(list_subdirectories(item_path))
    return subdirectories

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

def convert_md_to_json(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            md_filename = os.path.join(directory, filename)
            json_filename = os.path.splitext(md_filename)[0] + '.json'
            md_to_json(md_filename, json_filename)

def main():
    current_directory = os.getcwd()
    subdirectories = list_subdirectories(current_directory)
    subdirectories.append(current_directory)
    for subdir in subdirectories:
        convert_md_to_json(subdir)

if __name__ == "__main__":
    main()
