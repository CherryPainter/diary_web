print('-------------欢迎使用10086查询功能-------------')
print('1.查询当前余额')
print('2.查询当前流量')
print('3.查询当前通话剩余时长')
print('0.退出系统')
user_input = input('请输入您要查询的操作：')
while user_input > "3":
    if user_input > '3':
        print('对不起，您的输入有误！')
        user_input = input('请输入您要查询的操作：')
        print('-------------欢迎使用10086查询功能-------------')
        print('1.查询当前余额')
        print('2.查询当前流量')
        print('3.查询当前通话剩余时长')
        print('0.退出系统')
while user_input <= "3":
    print('----------------10086查询功能列表-----------------')
    print('1.查询当前余额')
    print('2.查询当前流量')
    print('3.查询当前通话剩余时长')
    print('0.退出系统')
    if user_input == '1':
        print('**当前余额为：234.5 元**')
        user_again_input = input('·还要继续操作吗？y/n')
        if user_again_input == 'y':
            user_input = input('请输入您要查询的操作：')
        elif user_again_input == 'n':
            print('程序退出，谢谢您的使用！')
            break
    elif user_input == '2':
        print('**当前剩余流量为：4 GB**')
        user_again_input = input('·还要继续操作吗？y/n')
        if user_again_input == 'y':
            user_input = input('请输入您要查询的操作：')
        elif user_again_input == 'n':
            print('程序退出，谢谢您的使用！')
            break
    elif user_input == '3':
        print('**当前剩余通话时长为：200 分钟**')
        user_again_input = input('·还要继续操作吗？y/n')
        if user_again_input == 'y':
            user_input = input('请输入您要查询的操作：')
        elif user_again_input == 'n':
            print('程序退出，谢谢您的使用！')
            break
    elif user_input == '0':
        print('程序退出，谢谢您的使用！')
        break
