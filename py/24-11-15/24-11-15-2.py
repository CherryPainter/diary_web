'1.打印字符串'
print('Hello Python!')

'2.数据类型判断'
x=eval(input('请输入一个值：'))
print(type(x))

y=1
print(type(y))

z=2.2
print(type(z))

a='I LOVE'
print(type(a))

'3.简单计算'
#和
a=1
b=2
c=a+b
print(c)
#差
d=b-a
print(d)
#积
e=a*b
print(e)
#商
f=a/b
print(f)

'4.判断奇偶性'
g=eval(input('请输入一个整数：'))
if g%2==0:
    print(g,'是一个偶数')
else:
    print(g,'是一个奇数')

'5.计算阶乘'
h=eval(input('请输入一个整数：'))
s=1
for i in range(1,h+1):
    s*=i
    print(h,'的阶乘是',s)

'6.求列表最大值'
t=[23,45,12,78,56]
max_num=t[1]
for i in range(len(t)):
    if t[i]>max_num:
        max_num=t[i]
        print(max_num)
#网上找的方法不知道原理，望求解

