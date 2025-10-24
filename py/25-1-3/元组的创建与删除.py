# 直接使用（）创建元组
t=('hello',[12,13,14],'python','word')
print(t)

# 使用函数（内置函数）tuple()创建元组
t1=tuple('helloworld')
print(t1)

t2=tuple([12,13,14])
print(t2)

t3=tuple(range(1,10))
print(t3)
print('len:',len(t3))
print('max',max(t3))
print('min',min(t3))
print('index',t3.index(4))
print('count', t3.count(4))

t4=(1,2,3,4,5,6,7,8,9,0)
del t4
print(t4)