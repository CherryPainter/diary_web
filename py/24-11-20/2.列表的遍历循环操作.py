x=['hello','world','python','PHP']

# 使用遍历循环
for item in x:
    print(item)

print('-'*40)

# 使用遍历循环for与range（）函数与len（）函数组合遍历
for i in range(0,len(x)):
    print(i,'--->',x[i])

print('-'*40)

# 遍历循环for与enumerate()函数组合遍历元素和索引
for index,item in enumerate(x):  # 默认序号从0开始
    print(index,'--->',item)
print('-'*40)
for index,item in enumerate(x,10000):  # 设置序号从10000开始
    print(index,'--->',item)