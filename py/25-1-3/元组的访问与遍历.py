t=('python','java','c++','javascript','ruby','php')
print(t[0])  # 根据索引访问
t2=t[0:6:2]  # 元组支持切片操作
print(t2)

print('----------------------------------------------')

# for+range()+len()组合遍历
for i in range(0,len(t)):
    print(i,t[i])

# 使用enumerate()
for indx,item in enumerate(t,):  #在（t,这里添加数字是改变其序号的开始)
    print(indx,'---->',item)