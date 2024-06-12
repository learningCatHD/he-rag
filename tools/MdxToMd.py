import os
import re

def remove_jsx_from_mdx(mdx_content):
    # 正则表达式匹配JSX标签的模式
    jsx_pattern = r'<\s*[a-zA-Z][^\s>]*[^>]*>.*?<\s*/\s*[a-zA-Z][^\s>]*\s*>'
    
    # 使用正则表达式替换JSX语法部分为空字符串
    md_content = re.sub(jsx_pattern, '', mdx_content, flags=re.DOTALL)
    
    return md_content

def convert_mdx_to_md(mdx_filename):
    # 读取MDX文件内容
    with open(mdx_filename, 'r', encoding='utf-8') as mdx_file:
        mdx_content = mdx_file.read()
    
    # 删除MDX文件中的JSX语法部分
    md_content = remove_jsx_from_mdx(mdx_content)
    
    # 构建MD文件名
    md_filename = mdx_filename[:-4] + '.md'
    
    # 将处理后的内容写入到新的.md文件中
    with open(md_filename, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)

def convert_directory_mdx_to_md(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.mdx'):
            mdx_filename = os.path.join(directory, filename)
            convert_mdx_to_md(mdx_filename)

def main():
    directory = os.getcwd()
    convert_directory_mdx_to_md(directory)

if __name__ == "__main__":
    main()
