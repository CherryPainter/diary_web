"""
apple = 8.5
user = float(input('请输入购买的公斤数:'))
print(apple * user, '元')
"""

"""input函数版
price = input("请输入苹果的价格：")
weight = input('请输入苹果的重量：')
money = float(price) * float(weight)
print(money, '元')
"""
#  格式化字符串版
price = float(input('请输入苹果的价格：'))
weight = float(input('请输入苹果的重量：'))
money = price * weight
print('-·'*20)
print('苹果单价：%.01f 元/斤' % price)
print('购买数量：%.02f 斤' % weight)
print('需要支付金额：%.02f 元' % money)
print('-·'*20)