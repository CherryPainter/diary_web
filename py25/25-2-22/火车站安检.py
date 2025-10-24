user = input('您是否有票？（y/n）:')
knife_length = 35
if user == 'y':
    print('-----正在进行安检-----')
    if knife_length <= 20:
        print('安检通过，请上车！')
    elif knife_length > 20:
        print('不好意思乘客，您的刀具长 %d 厘米，超过了规定的20厘米，不能带上车.' % knife_length)
else:
    print('请购票！')
