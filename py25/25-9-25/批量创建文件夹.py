import os


def create_dir(path, num):
    if not os.path.exists(path):
        os.mkdir(path)
    for dirs in range(1, num + 1):
        os.mkdir(os.path.join(path, str(dirs)))




create_dir(r'D:\Learn\data\py25\25-9-25\dir', 3)