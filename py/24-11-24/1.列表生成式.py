import random
a=['apple','banana','cherry']
print(a)
print(max(a))
print(min(a))
a.clear()
print(a)


new_a=a=[i for i in range(1,11)]
print(new_a)

news_a=a=[i*i for i in range(1,11)]
print(news_a)

newss_a=[random.randint(1,10) for _ in range(10) ]
print(newss_a)