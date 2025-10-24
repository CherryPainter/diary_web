cards_list = []


def add_business_cards(name, phone, email, addres):
    """
    # 新建名片模块
    :param name: 名字
    :param phone: 手机号
    :param email: 电子邮箱
    :param addres: 地址
    :return: NONE
    """
    # 创建一个字典，包含名片的各项信息
    # 使用关键字参数创建字典，键值对分别为名片的各种属性
    cards_dict = dict(name=name,  # 字典创建（红色为key，等号后是value）
                      phone=phone,
                      email=email,
                      address=addres)
    # 将创建好的字典追加到全局列表cards_list中
    cards_list.append(cards_dict)  # 追加数据
    # 打印写入成功的提示信息
    print('----------写-入-成-功-！----------')


def all_cards():
    """
    显示全部模块

    该函数用于显示所有存储的联系人的信息
    :return: 无返回值
    """
    print('\n\n')  # 打印两个空行，用于格式化输出
    print("-" * 75)  # 打印75个"-"字符，作为分隔线
    if len(cards_list) == 0:  # 检查cards_list是否为空
        print('抱歉，没有数据存储！')  # 如果为空，提示没有数据
    else:
        # 打印表头，使用format方法进行格式化输出
        print("{:<10}{:^15}{:^15}{:>15}".format("姓名", "手机号", "电子邮箱", "地址"))
        print("=" * 75)  # 打印75个"="字符，作为表头与内容的分隔线
        # 遍历cards_list，打印每个联系人的信息
        for i in cards_list:
            # 使用format方法格式化输出每个联系人的信息
            print("{:<10}{:^15}{:^18}{:>18}".format(i['name'], i['phone'], i['email'], i['address']))
    print("-" * 75)  # 打印75个"-"字符，作为结束分隔线
    print('\n\n')  # 打印两个空行，用于格式化输出


def query_modify_delete_mod(card):
    """
    查改删模块
    :param card: 查询的名片名称
    :return: NONE
    """
    # cards(变量)循环值大致是按下标来算
    for cards in cards_list:
        # card(目标)和 cards(变量) 相等时进行下一步
        if card == cards['name']:
            print('找到 %s \n' % card, cards)
            select = input('是否删改？（1.修改 2.删除 [回车跳过])')
            # 修改模块
            if select == '1':
                name = input('请输入姓名[回车跳过]：') or cards['name']  # [重点]逻辑符号 or 是为了使后面使用 .update() 合并字典时，不让空值覆盖原值。
                phone = input('请输入电话[回车跳过]：') or cards['phone']
                email = input('请输入电子邮件[回车跳过]：') or cards['email']
                address = input('请输入住址[回车跳过]：') or cards['address']
                # 定义临时字典存储数据（红色为key，等号后是value）
                dicts = dict(name=name,
                             phone=phone,
                             email=email,
                             address=address)
                # 临时变量储存全局变量的目标字典的索引值
                x = cards_list.index(cards)
                # 合并字典（对已有键覆盖，反之合并）
                cards_list[x].update(dicts)
                print('-------修-改-成-功-！-------')
                return
            # 删除模块
            elif select == '2':
                # 临时变量储存全局变量的目标字典的索引值
                x = cards_list.index(cards)
                # .pop() 删除指定索引数据
                cards_list.pop(x)
                print('-------删-除-成-功-！-------')
            else:
                # 处理异常输入，避免程序崩溃
                print('-------选择不合法，请重新选择！-------')
                continue
    else:
        print('-------抱歉！没有此用户卡片-------')
