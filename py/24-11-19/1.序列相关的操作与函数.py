a = 'hello world'
# x in s
print('r是hello world中存在吗？', ('r' in a))
print('v在hello world中存在吗？', ('v' in a))  # print里的括号是提高优先级的意思

print('-' * 40)

# x not s  取反或者否定
print('x不是a的元素吗？', ('l' not in a))  # l是a的元素故为false
print('v不是a的元素吗？', ('v' not in a))  # v不是a的元素故为true

print('-' * 40)

# len（s） /   max（s）  / min (s)
print(len(a))
print(max(a))  # 最大最小看的是unico码的大小
print(min(a))

print('-'*40)

# 序列对象的方法  使用序列的名称打点调用
# s.index(x)   / s.count(x)
print('d在字符串序列中的第', a.index('d'), '位')
print('o在a中出现了', a.count('o'),'次。')

print('-'*40)