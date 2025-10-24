# 打印 1 到 10
# 要求：用 for 和 while 各写一次，把 1 到 10 依次打印出来。
for i in range(11):
    print(i)

print("-" * 50)

a = 1
while a <= 10:
    print(a)
    a += 1

print("-" * 50)

# 计算 1 到 100 的和
# 要求：用 for 或 while 计算 1 + 2 + 3 + ... + 100 的和，并打印结果。
c = 0
for b in range(101):
    c += b
print(c)

d = 1
e = 0
while d <= 100:
    e += d
    d += 1
print(e)

print("-" * 50)

# 统计 100 以内的偶数个数
# 要求：使用 for 或 while 统计 1~100 之间有多少个偶数，并打印出来。
g = 0
for f in range(101):
    if f % 2 == 0 and f != 0:
        g += 1
print('100以内的偶数有 %d' % g)

h = 1
j = 0
while h <= 100:
    if h % 2 == 0:
        j += 1
    h += 1
print('100以内的偶数有 %d' % j)

print("-" * 50)

# 乘法表
# 要求：用 for 循环打印九九 乘法表
l = 1
for k in range(1, 10):
    for i in range(k):
        print('%d * %d = %d' % (l, k, l * k), end='\t')
        l += 1
    l = 1
    print('')
print("-" * 50)
# 拓展用while打印九九乘法表。
e = 1
while e < 10:
    r = 1
    while r <= e:
        print('%d * %d = %d' % (r, e, r * e), end='\t')
        r += 1
    print('')
    e += 1

print("-" * 50)

# 反向打印星星
# 要求：输入一个整数 n，打印 n 行星星，每一行的星星数量依次减少。
u = int(input('请输入要打印的星星行数：'))
for xc in range(0, u):
    for _ in range(0, u - xc):
        print('*', end='')
    print('')

print("-" * 50)

# 找出 1~100 之间的所有质数
# 要求：使用 for 循环找出 1 到 100 之间的所有质数（只能被 1 和自身整除的数）。
