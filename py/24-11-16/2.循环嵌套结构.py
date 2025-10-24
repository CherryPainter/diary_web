# 请输出一个菱形
lx = input('请输入菱形的行数:')
top_lx = (int(lx) + 1) // 2  # input的整数是菱形的总长度，为实现它，必要将菱形分为两个部分（上下），所以整除（//）2为两份。
for i in range(1, top_lx + 1):  # 运用range函数，首先range函数取头不取尾，所以要加一，代表在1，top_lx中依次循环
    # 首先要建立一个倒三角空白选区搭建结构，top_lx+1-i的意思是当i=1时 top_lx==4时，for j in range(1,4-1)
    # for j in range(1,4-1)大意为range生成区间（1，2，3]，在这一次循环中内循环2次
    # 可知当n-i时数值是由大变小的。
    for j in range(1, top_lx + 1 - i):
        print(' ', end='')
    # 当i=1时 for k in range(1,2),循环1次，并打印一个点。
    # 可知当i*n（未知数）时数据会累加直到循环结束
    for k in range(1, i * 2):
        print('*', end='')
    print()
down_lx = (int(lx)) // 2
for i in range(1, down_lx):
    for j in range(1, i + 1):
        print(' ', end='')
    # 审核遇到的问题下三角形是一个递减的每一行比下一行少两个*，我们分析可知，假设整个菱形是8，那么down_lx=4,第一行（1，5）第二行为（2，3）第三行为（3.1）
    # range(1,6) range(1,4) range(1,2)=2*3 2*2 2*1 找到2为公倍数，那我们则可根据down_lx-i可得，当down_lx=4时i=1时可知4-1=3
    # 总而言之得出公式为range(1,2*(down_lx-i))
    for k in range(1, 2 * (down_lx - i)):
        print('*', end='')
    print()
