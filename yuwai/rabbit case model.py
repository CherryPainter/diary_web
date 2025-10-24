rabbit = 3
print("请输入n的值")
n = int(input())
for i in range(0, n):
    rabbit = rabbit * 2
    print("%d年后,兔子的数量%d" % (i, rabbit))
