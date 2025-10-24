#  打印99乘法表
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j} * {i} = {i * j}",end='\t')
    print()

r = 0
for i in range(1,101):
    if i % 2 == 0:
        r += i
print(f"1到100的偶数和为：{r}")

n = 1
result = 0
while n <= 100:
    if n % 2 == 0:
        result += n
    n += 1
print(f"1到100的偶数和为：{r}")


import time


numbers = int(input("请输入一个整数："))
for i in range(numbers):
    time.sleep(1)
    countdown = numbers - i
    print(f"倒计时：{countdown}秒")
    if countdown == 1:
        print("时间到！")

arr = input("请输入一组数据：").split(',')
i = 1
j = 0
for i in range(len(arr)):
    for j in range(len(arr) - 1):
        if int(arr[j]) > int(arr[j + 1]):
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
print(f"最大值是：{arr[-1]}")

for i in range(1, 10):
    for j in range(1, i + 1):
        print(j, end='\t')
    print()


import random


randoms = random.randint(1, 100)
while True:
    guess = int(input("请输入一个1到100之间的整数："))
    if guess > randoms:
        print(f"猜大了")
    elif guess < randoms:
        print("猜小了")
    else:
        print("恭喜你，猜对了！")
        break

arr = [1, 2, 2, 3, 3, 4]
result = list(set(arr))
print(result)  # [1, 2, 3, 4] （顺序可能改变）
# 不想改变顺序就
result.sort(key= arr.index)