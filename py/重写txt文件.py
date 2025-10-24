import os


def sanitize_path(path):
    """将路径中的反斜杠转化为系统合适的分隔符"""
    return os.path.normpath(path)


def is_valid_file(file_path):
    """检测文件路径是否合法"""
    return os.path.isfile(file_path)


def rewrite_txt_file(src_file_path, dest_folder):
    """将源文件的内容重写到目标文件夹并生成同名文件"""
    # 检查源文件是否存在
    if not is_valid_file(src_file_path):
        print(f"源文件 {src_file_path} 不存在或路径无效")
        return

    # 获取源文件名
    file_name = os.path.basename(src_file_path)

    # 创建目标文件的完整路径
    dest_file_path = os.path.join(dest_folder, file_name)

    # 打开源文件进行读取
    with open(src_file_path, 'r', encoding='utf-8') as src_file:
        content = src_file.read()

    # 对内容进行重写，可以在此进行任何处理
    modified_content = content  # 这里只是简单的重写，按需求修改

    # 确保目标文件夹存在
    os.makedirs(dest_folder, exist_ok=True)

    # 将修改后的内容写入目标文件
    with open(dest_file_path, 'w', encoding='utf-8') as dest_file:
        dest_file.write(modified_content)

    print(f"文件已重写并保存到 {dest_file_path}")


def process_files():
    """主处理逻辑，支持单文件和批量文件操作"""
    # 获取用户输入
    src_folder = input("请输入源文件夹路径：")
    dest_folder = input("请输入目标文件夹路径：")

    # 处理路径格式
    src_folder = sanitize_path(src_folder)
    dest_folder = sanitize_path(dest_folder)

    # 获取文件类型（单文件/批量）
    mode = input("选择操作方式：单一文件 (1) 或 批量文件 (2)：")

    # 单文件操作
    if mode == '1':
        src_file = input("请输入单个源文件路径：")
        src_file = sanitize_path(src_file)
        rewrite_txt_file(src_file, dest_folder)

    # 批量文件操作
    elif mode == '2':
        # 获取源文件夹中的所有txt文件
        if os.path.isdir(src_folder):
            files = [f for f in os.listdir(src_folder) if f.endswith('.txt')]
            if not files:
                print(f"在文件夹 {src_folder} 中没有找到 .txt 文件。")
                return

            # 对每个文件进行处理
            for file in files:
                src_file_path = os.path.join(src_folder, file)
                rewrite_txt_file(src_file_path, dest_folder)
        else:
            print(f"源文件夹 {src_folder} 路径无效或不存在。")
    else:
        print("无效的选项。请重新选择操作方式。")


# 运行主处理逻辑
process_files()
