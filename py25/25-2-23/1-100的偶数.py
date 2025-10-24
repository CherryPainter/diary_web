i = 0
s = 0
r = 0
while i <= 100:
    i += 1
    if i % 2 == 0:
        r += i
        s += 1
print('1-100是偶数的有：%d 个' % s)
print('1-100偶数的累加和是：%d ' % r)
