nums = [2, 5, 8, 3, 10, 7]
s = 0
i = 0
for i in nums:
    s += i
y = s / len(nums)
for i in nums:
    if i > y:
        print(i, end=' ')
