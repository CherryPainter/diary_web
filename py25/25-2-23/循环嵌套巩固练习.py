# 打印正方形
i = 1
for i in range(5):
    for j in range(5):
        print('*', end='')
    print('')

print('-' * 50)
# 打印右上直角三角形
a = 1
while a <= 5:
    b = 1
    while b <= a:
        print('*', end='')
        b += 1
    a += 1
    print('')

print('-' * 50)
# 打印倒直角三角形
c = 1
while c <= 5:
    for d in range(6 - c):
        print('*', end='')
    print('')
    c += 1

print('-' * 50)
# 打印等腰三角形
e = 1
while e <= 5:
    for f in range(6 - e):
        print(' ', end='')
    for j in range(2*e-1):
        print('*', end='')
    print('')
    e += 1

print('-' * 50)
# 打印倒等腰三角形
h = 1
n = 5
while h <= 5:
    l = 1
    while l <= h:
        print(' ', end='')
        l += 1
    for m in range(2 * n - 1):
        print('*', end='')
    n -= 1
    print('')
    h += 1

print('-' * 50)
# 打印菱形
z = 1
o = 4
while z <= 5:
    for v in range(6-z):
        print(' ', end='')
    for m in range(2 * z -1):
        print('*', end='')
    print('')
    z += 1
cw = 1
while cw <= 4:
    for t in range(cw+1):
        print(' ', end='')
    for u in range(o * 2 - 1):
        print('*', end='')
    o -= 1
    cw += 1
    print('')



