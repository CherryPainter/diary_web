def fac(n):
    if n == 1:
        return 1
    else:
        return n * fac(n - 1)


num = int(input('请输入一个正整数：'))
print(f"{num}的阶乘是{fac(num)}")
