# 处理累加和小于50的
s = 0
i = 1
while i <= 20:
    s += i
    if s > 110:
        print(i)
        break
    i += 1
print('-----------------------------------------------------')
i = 0
while i < 4:
    user_name = input("请输入您的用户名：")
    pwd = input("请输入您的密码:")
    if user_name == '郭子玘' and pwd == '123456':
        print('正在登陆系统……')
        break
    else:
        if i<4:
            print('密码错误！您还有', 3 - i, '次机会')
    i+=1
else:
    print('----------账号已锁定！----------')
