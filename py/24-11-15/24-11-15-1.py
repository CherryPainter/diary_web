x = eval(input('请选择你要转换的进制：（八进制=8，十六进制=16，二进制=2）'))
y = eval(input('请输入所需处理的数据:'))
if and x == '2':
    print(bin(y))
elif int and x == '8':
    print(oct(y))
elif type(y) == int :
    print(hex(y))
elif type(y) == str:
    print('数据错误请重新运行')
elif type(y) == float:
    print('数据错误请重新运行')
else:
    print('数据错误请重新运行')

