year=input('请输入一个需要判断的年份：')
if int(year)%4==0 or int(year)%400==0 and int(year)%100!=0:
    print(year,'是闰年')
else:
    print(year,'是平年')