import os
import json

def sanitize_path(path):
    """
    将用户输入的路径格式标准化为合法路径。
    """
    return path.strip('"').replace("\\", "/")

def get_valid_path(prompt):
    """
    获取用户输入的合法路径，并校验其是否存在。
    """
    while True:
        path = input(prompt).strip()
        path = sanitize_path(path)
        if os.path.exists(path):
            return path
        else:
            print("路径不存在，请重新输入！")

def get_txt_files(path):
    """
    获取路径下的所有txt文件。
    """
    txt_files = [file for file in os.listdir(path) if file.endswith('.txt')]
    if not txt_files:
        print(f"路径 '{path}' 下没有找到任何txt文件。")
    return txt_files

def read_json_file(file_path):
    """
    读取JSON格式的txt文件，返回解析的字典。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"文件 {file_path} 读取失败：{e}")
        return None

def write_json_file(file_path, data):
    """
    将字典数据写回到JSON格式的txt文件。
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"文件 {file_path} 写入失败：{e}")

def process_file(read_path, replace_path, key):
    """
    替换单个文件中对应量名的值。
    """
    read_data = read_json_file(read_path)
    replace_data = read_json_file(replace_path)

    if read_data is None or replace_data is None:
        return False

    # 检查读取文件是否包含指定量名
    if key in read_data:
        value_to_replace = read_data[key]  # 从读取文件中获取值
        print(f"从读取文件中找到的值：{key} -> {value_to_replace}")
        # 如果替换文件中没有该量名，新建该量名
        if key not in replace_data:
            print(f"替换文件中不存在量名 '{key}'，将自动添加。")
        replace_data[key] = value_to_replace
        # 写回替换文件
        write_json_file(replace_path, replace_data)
        print(f"文件 '{replace_path}' 中的 '{key}' 已成功替换为 '{value_to_replace}'！")
        return True
    else:
        print(f"读取文件中未找到量名 '{key}'，跳过。")
        return False

def main():
    while True:
        # 获取读取路径和替换路径
        print("请输入读取路径：")
        read_dir = get_valid_path("读取路径：")
        print("请输入替换路径：")
        replace_dir = get_valid_path("替换路径：")

        # 获取读取路径和替换路径的txt文件
        read_files = get_txt_files(read_dir)
        replace_files = get_txt_files(replace_dir)

        if not read_files or not replace_files:
            print("无法继续操作，因为路径下缺少txt文件。")
            return

        print(f"读取路径下的文件：{read_files}")
        print(f"替换路径下的文件：{replace_files}")

        while True:
            # 用户输入量名
            key = input("请输入要替换的量名（如 unitName）：").strip()

            # 是否批量操作
            is_batch = input("是否进行批量操作？(是/否)：").strip().lower()
            if is_batch == "是":
                for read_file, replace_file in zip(read_files, replace_files):
                    read_path = os.path.join(read_dir, read_file)
                    replace_path = os.path.join(replace_dir, replace_file)
                    process_file(read_path, replace_path, key)
            else:
                read_file = input(f"请输入读取文件名(从 {read_files} 中选择)：").strip()
                replace_file = input(f"请输入替换文件名(从 {replace_files} 中选择)：").strip()

                if read_file in read_files and replace_file in replace_files:
                    read_path = os.path.join(read_dir, read_file)
                    replace_path = os.path.join(replace_dir, replace_file)
                    process_file(read_path, replace_path, key)
                else:
                    print("文件名无效，请重新输入。")
                    continue

            # 是否继续替换其他量名
            continue_replace = input("是否替换其他量名？(是/否)：").strip().lower()
            if continue_replace != "是":
                break

        # 是否从新路径开始
        restart = input("是否从新路径开始操作？(是/否)：").strip().lower()
        if restart != "是":
            print("操作结束，感谢使用！")
            break

if __name__ == "__main__":
    main()
