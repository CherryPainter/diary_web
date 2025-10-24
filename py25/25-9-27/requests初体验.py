import requests
from bs4 import BeautifulSoup
url = 'https://kb.chaoxing.com/res/pc/curriculum/schedule.html?curriculumUuid=28374639-1748-4184-ae23-6c653849c93b'
# 反爬虫用的请求头
header = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
}

resp = requests.get(url, headers=header)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')
box = soup.find('div', class_='table')
print(box)