arr = [1, 4, 2, 3, 3, 4]
result = list(set(arr))
print(result)  # [1, 2, 3, 4] （顺序可能改变）
# 不想改变顺序就
result.sort(key=arr.index)
