# 基础循环知识
i = 1
while i <= 5:
    print('*'*i)
    i += 1

print('-'*20)
# 循环嵌套
row = 1
while row <= 5:
    k = 1
    while k <= row:
        print('*',end='')
        k += 1
    print('')
    row += 1