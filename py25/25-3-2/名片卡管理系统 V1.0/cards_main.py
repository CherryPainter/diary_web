import cards_tools


def main():
    """
    名片管理系统的主函数，实现系统的核心逻辑和用户交互
    包含主菜单显示、功能选择和相应的操作调用
    """
    while True:
        print('*' * 40)  # 打印分隔线
        print('欢迎使用【名片管理系统】V1.1')  # 打印系统标题
        print('')  # 打印空行，用于格式化
        print("1. 新建名片")  # 显示功能选项1
        print('2. 显示全部')  # 显示功能选项2
        print('3. 查询名片')  # 显示功能选项3
        print('')  # 打印空行，用于格式化
        print('0. 退出系统')  # 显示退出选项
        print('*' * 40)  # 打印分隔线
        print('')  # 打印空行，用于格式化
        User_Action = input('请选择要使用的功能：')  # 获取用户输入的功能选择
        # 新建名片模块
        if User_Action == '1':  # 判断用户是否选择新建名片
            cards_tools.add_business_cards(  # 调用添加名片函数
                name=input('请输入姓名：'),  # 获取用户输入的姓名
                phone=input('请输入电话：'),  # 获取用户输入的电话
                email=input('请输入电子邮件：'),  # 获取用户输入的电子邮件
                addres=input('请输入住址：')  # 获取用户输入的住址
            )
        # 显示全部模块
        elif User_Action == '2':  # 判断用户是否选择显示全部名片
            cards_tools.all_cards()  # 调用显示全部名片函数
        # 查改删模块
        elif User_Action == '3':  # 判断用户是否选择查询名片
            cards_tools.query_modify_delete_mod(  # 调用查询修改删除函数
                card=input('请输入想要查询的名片：'))  # 获取用户输入的查询内容
        # 处理异常输入，避免程序崩溃
        elif User_Action not in ['0', '1', '2', '3']:  # 判断用户输入是否为有效选项
            print('')  # 打印空行，用于格式化
            print('--------请输入正确的功能！--------')  # 提示用户输入正确的功能选项
            print('')  # 打印空行，用于格式化
        # 程序运行结束
        else:  # 用户选择退出系统
            print('-----感谢您的使用！-----')  # 显示退出提示
            break  # 退出循环，结束程序


if __name__ == '__main__':
    main()
