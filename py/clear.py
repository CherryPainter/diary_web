import os
import re

def clean_invisible_chars(text):
    """清理文本中的空格和不可见字符"""
    return re.sub(r'[\u200b\u200c\u200d\u2060\ufeff\xa0]+', '', text).strip()

def process_file(file_path, output_path):
    """清理单个文件中的不可见字符并输出到指定路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        cleaned_content = clean_invisible_chars(content)

        # 写入输出路径
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"文件已清理并保存至: {output_path}")
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")

def process_files(input_paths, output_dir):
    """批量处理文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path in input_paths:
        if not os.path.isfile(file_path):
            print(f"跳过无效路径: {file_path}")
            continue

        file_name = os.path.basename(file_path)
        output_path = os.path.join(output_dir, file_name)
        process_file(file_path, output_path)

if __name__ == "__main__":
    # 使用 input 获取用户输入
    input_path = input("请输入文件或文件夹路径: ").strip()
    output_dir = input("请输入输出文件夹路径: ").strip()

    input_paths = []
    if os.path.isdir(input_path):
        # 如果是文件夹，获取所有文件路径
        input_paths.extend([os.path.join(input_path, f) for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))])
    else:
        input_paths.append(input_path)

    # 批量处理文件
    process_files(input_paths, output_dir)
