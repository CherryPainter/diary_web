import os
import random


def create_filename():
    filename = []
    lst = ['水果', '蔬菜', '粮油', '肉蛋', '百货']
    code = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    for i in range(1,1001):
        file_num = f'{i:04d}'
        list_name = random.choice(lst)
        s = ''.join(random.choice(code) for _ in range(10))
        filename.append(file_num + list_name + '_' + s)
    return filename


def create_file(path, filename):
    if not os.path.exists(path):
        os.makedirs(path)

    for file_name in filename:
        file_path = os.path.join(path, file_name) + '.txt'
        with open(file_path, 'w') as f:
            pass
    print('文件生成完成啦~')


create_file(r'D:\Learn\data\py25\25-9-25\Material', create_filename())






