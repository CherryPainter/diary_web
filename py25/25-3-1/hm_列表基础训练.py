# 创建列表
# 创建一个包含 "苹果", "香蕉", "樱桃" 的列表，并打印它。
sg_list = ['苹果', '香蕉', '樱桃']
print(sg_list)

print('*' * 50)

# 索引访问
# 给定列表 fruits = ["苹果", "香蕉", "樱桃", "橙子", "葡萄"]，请获取并打印：
fruits = ["苹果", "香蕉", "樱桃", "橙子", "葡萄"]
print('第一个元素：',fruits[0] , '第二个元素：',fruits[-1])

print('*' * 50)

# 列表切片
# 取出 fruits 列表的前三个元素，并打印它们。
print(fruits[:3])

print('*' * 50)

# 修改列表
# 继续使用 fruits 列表，把 "香蕉" 改成 "蓝莓"，然后打印修改后的列表。
fruits[1] = "蓝莓"
print(fruits)

print('*' * 50)

# 添加元素
# 在列表末尾添加 "西瓜"
# 在索引 2 位置插入 "梨"
# 打印修改后的列表
fruits.append("西瓜")
fruits.insert(2,"梨")
print(fruits)

print('*' * 50)

# 删除元素
# 使用 del 语句删除 "樱桃"
# 使用 .remove() 方法删除 "葡萄"
# 使用 .pop() 方法删除最后一个元素，并打印它
del fruits[3]
print(fruits)
fruits.remove("葡萄")
print(fruits)

print('*' * 50)

# 列表拼接
# 创建另一个列表 more_fruits = ["柠檬", "草莓"]，把它与 fruits 合并并打印。
more_fruits = ["柠檬", "草莓"]
fruits.extend(more_fruits)
print(fruits)

print('*' * 50)

# 查找元素
# 检查 "苹果" 是否在 fruits 列表中，如果存在，打印 "找到苹果！"，否则打印 "苹果不在列表中"。
if "苹果" in fruits:
    print('找到苹果！')
else:
    print("苹果不在列表中")

print('*' * 50)

# 列表遍历
# 使用 for 循环遍历 fruits，并逐行打印每个水果的名字。
for fruit in fruits:
    print(fruit)

#  列表推导式
# 给定 numbers = [1, 2, 3, 4, 5]，请使用 列表推导式 创建一个新列表 squared，其中每个元素是原列表中数字的平方，并打印它。
numbers = [1, 2, 3, 4, 5]