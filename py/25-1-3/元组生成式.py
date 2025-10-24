t=(i for i in range(1,11)) #结果是一个生成式
print(t)
t=tuple(t)
print(t)

for item in t:
    print(item)
