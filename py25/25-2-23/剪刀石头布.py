import random
print('------剪刀石头布！------')
print('石头（1）/剪刀（2）/布（3）')
user = int(input('请输入指代的编号：'))
pc = random.randint(1,3)
print('-' * 21)
if user >= 4 or user <= 0:
    print('请输入合法编号！！！')
else:
    print('玩家选择出的拳是 %d,电脑选择出的拳是 %d' % (user, pc))
    if user == pc:
        print('平局')
    elif ((user == 1 and pc == 2)
          or (user == 2 and pc == 3)
          or (user == 3 and pc == 1)):
        print('玩家获胜！')
    else:
        print('电脑获胜！')