import os

# 使用 os 模块获取当前工作目录，并打印出来。
print(os.getcwd())
# 使用 os 模块列出当前目录下的所有文件和文件夹。
print(os.listdir(path=r"D:\Learn\data\py25"))


# 写一个程序，判断一个路径是文件还是文件夹。
def judge_path(path):
    if os.path.isfile(path):
        print(f"{path} 是一个文件")
    if os.path.isdir(path):
        print(f"{path} 是一个文件夹")


judge_path(r"D:\Learn\date")


# 创建一个名为 test_dir 的文件夹，如果已存在就提示“文件夹已存在”。
def create_dir(path):
    if os.path.exists(path):
        print("文件夹已存在")
    else:
        os.mkdir(path)
        print(f"文件夹 {path} 创建成功")


# create_dir("test_dir")

# 在 test_dir 文件夹里新建一个文件 hello.txt。
def create_file(path):
    if os.path.exists(path):
        print('文件已存在哦!')
    else:
        with open(path, 'w', encoding='UTF-8') as f:
            f.write('hello world')
            print(f"文件 {path} 创建成功")


create_file('hello.txt')


# 写一个程序，遍历打印指定文件夹下的所有文件（包括子文件夹中的）。
def print_all_file(path):
    for file in os.listdir(path):
        print(file)
        print('-' * 10)
        inner_file = os.path.join(path, file)
        for files in os.listdir(inner_file):
            if os.path.isdir(files):
                print_all_file(files)
            else:
                print(files)
        print('-' * 30)


print_all_file(r'D:\Learn\data\py25')


# 写一个函数，统计某个目录下所有 .txt 文件的数量。
def count_all_file(path, cla):
    cla = cla
    count = 0
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            count += count_all_file(file_path, cla)
        elif file.endswith(cla):
            count += 1
    return count


path = r'D:\Learn\data\py25'
cla = '.txt'
total = count_all_file(path, cla)
print(f'{path}里有{total}个{cla}文件')

print('-' * 50)


# 使用 os.path 模块获取一个文件的：
#
# 文件名
#
# 文件所在目录
#
# 文件后缀
#
# 写一个程序，获取某个文件的大小（单位：字节）。
#
# 删除一个指定的空文件夹，并确保不会误删非空文件夹。
def judge_path(path):
    if os.path.exists(path):
        if not os.listdir(path):
            os.rmdir(path)
            print(f'指定{path}文件下的目录为空已删除！')
        else:
            print(f'指定{path}文件下的目录不是空的哦！')
    else:
        print(f'指定{path}文件不存在！')


def del_file(path):
    judge_path(path)
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        judge_path(file_path)


del_file(r'D:\Learn\data\py25')
