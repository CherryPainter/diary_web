#l = [1,2,3,4,5,6,7]
#print(l.pop(0), len(l))

a = 0
for i in range(1, 5):
    for j in range(1, 5):
        for k in range(1, 5):
            if i != j and j != k and i != k:
                print(f"{i}{j}{k}")
                a += 1
print(f"总共可以组成 {a} 个三位数")
# 定义元组 tu_num1
tu_num1 = ('p', 'y', 't', ['o', 'n'])

# 向元组最后一个列表中添加新元素 'h'
tu_num1[-1].append('h')

# 输出修改后的元组
print(tu_num1)
