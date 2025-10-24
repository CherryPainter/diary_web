import os
import shutil

# 定义源目录和目标目录
source_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(source_dir, 'dist')

# 确保dist目录存在
if not os.path.exists(dist_dir):
    print(f"错误：dist目录不存在，路径：{dist_dir}")
    exit(1)

# 需要复制的数据文件列表
data_files = [
    'word_dict.json',
    'USER_MANUAL.md',
    'DEVELOPER_DOCS.md'
]

# 创建audio_cache目录
audio_cache_dir = os.path.join(dist_dir, 'audio_cache')
if not os.path.exists(audio_cache_dir):
    os.makedirs(audio_cache_dir)
    print(f"创建audio_cache目录: {audio_cache_dir}")

# 复制每个数据文件
copied_count = 0
missing_files = []

for file_name in data_files:
    source_path = os.path.join(source_dir, file_name)
    target_path = os.path.join(dist_dir, file_name)
    
    if os.path.exists(source_path):
        shutil.copy2(source_path, target_path)
        copied_count += 1
        print(f"复制文件: {file_name} -> {target_path}")
    else:
        missing_files.append(file_name)
        print(f"警告：文件不存在: {source_path}")

# 特殊处理：如果word_dict.json不存在，创建一个基础版本
if 'word_dict.json' in missing_files:
    basic_dict = {
        "hello": {"translation": "你好", "category": "基础词汇", "weight": 1.0},
        "world": {"translation": "世界", "category": "基础词汇", "weight": 1.0}
    }
    target_dict_path = os.path.join(dist_dir, 'word_dict.json')
    import json
    with open(target_dict_path, 'w', encoding='utf-8') as f:
        json.dump(basic_dict, f, ensure_ascii=False, indent=2)
    print(f"创建基础word_dict.json文件: {target_dict_path}")
    copied_count += 1

print(f"\n复制完成！")
print(f"成功复制: {copied_count} 个文件")
if missing_files:
    print(f"缺失文件: {len(missing_files)} 个")

# 检查可执行文件是否存在
executable_path = os.path.join(dist_dir, '听写助手.exe')
if os.path.exists(executable_path):
    exe_size = os.path.getsize(executable_path) / (1024 * 1024)
    print(f"\n可执行文件信息:")
    print(f"路径: {executable_path}")
    print(f"大小: {exe_size:.2f} MB")
    print("\n应用程序已准备就绪！")
    print("您可以双击 '听写助手.exe' 来运行应用程序。")
else:
    print(f"\n错误：可执行文件不存在: {executable_path}")