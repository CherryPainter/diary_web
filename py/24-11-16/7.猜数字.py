import random

numbers = random.randint(1, 100)
count = 0
while count <= 10:
    num = input('我的心里啊！有一个数，请你猜一猜。')
    if int(num) == numbers:
        print('我就知道你是了解我的！ʕ⸝⸝⸝˙Ⱉ˙ʔ')
        break
    elif int(num) > numbers:
        print('虽然大了，不过还是接近我的内心了呢！( 灬 ╹ ω ╹ 灬 )')
    else:
        print('小了一点，不过你要自信我相信你！(,,◕ ⋏ ◕,,)')
    count = count + 1
if count <= 3:
    print('------------------------------------------')
    print('可能这就是命中注定了吧！ि०॰०ॢी♡')
elif count <= 6:
    print('------------------------------------------')
    print('你是我的知心好友，是我生命中重要的人|ૂ•ᴗ•⸝⸝)')
elif count <= 10:
    print('------------------------------------------')
    print('还好是你，让我等了那么久。꒰ ๑͒ ･౪･๑͒꒱')
else:
    print('------------------------------------------')
    print('可能你不是我要等的人吧。(｡╯︵╰｡)')
