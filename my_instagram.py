import requests
import re
import asyncio
import random
import aiohttp

class Instagram:
  __slots__ = ['token', 'debug']

  def __init__(self, token='0.21158621296914282', debug=False):  # Токен, который можно взять из браузера
    self.token = token
    self.debug = debug

  def get(self, url):
    if self.debug:
      print('start query to {}'.format(url))
    
    result = requests.get(url)
    if self.debug:
      print('end query to {}. result: {}'.format(url, result))

    return result.content.decode('cp1251', errors='ignore') 

  async def get_async(self, url):
    if self.debug:
      print('start async query to {}'.format(url))

    # TODO чтобы инстраграмм нас не блокировал
    asyncio.sleep(random.randint(0, 10) * 1e-2)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            return content

  def search(self, query: str):
    url = '''https://www.instagram.com/web/search/topsearch/?context=blended&query={}&rank_token={}&include_reel=true'''.format(
      query, self.token
    )

    return self.get(url)

  @staticmethod
  def get_telephone_from_page(content):
    regex_list = [
      r'\+7\d{6,}',
      r'[8|\+7]-\d+-\d+-\d+',
      r'[8|\+7] \d{2,} \d{2,} \d{2,}',
      r'[8|\+7]\d{3} \d{3} \d{2} \d{2}',
      r'[8|\+7]\(\d+\)\d+-\d+-\d+'
    ]
    telephones = []
    for regex in regex_list:
      telephones += re.findall(regex, content)
    return list(set(telephones))

  async def get_user_async(self, user_name):
    url = '''https://www.instagram.com/{}/'''.format(
        user_name
    )

    content = await self.get_async(url)
    return {
      'tel': self.get_telephone_from_page(content)
    }