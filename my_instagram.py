import requests
import re
import asyncio
import random
import aiohttp
import json

class LoadException(Exception): pass

class Instagram:
  __slots__ = ['token', 'debug']

  # toc = 0iFY1183fFEhhUD198QYhkmz4Cp7ootA
  # user_id = 1013029601

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

  async def get_async(self, url, level=0):
    if self.debug:
      print('start async query to {}'.format(url))

    # TODO чтобы инстраграмм нас не блокировал
    await asyncio.sleep(random.randint(0, 10) * 1e-2)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            if 'Page Not Found' in content:
              print('Page Not Found')
              if level >= 5:
                return LoadException()

              await asyncio.sleep(random.randint(0, 10) * 0.1)
              return await self.get_async(url, level+1)
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
      r'[8|\+7]\(\d+\)\d+-\d+-\d+',
      r'[8|\+7]9\d{9}',
      r'[8|\+7] \(\d{3}\) \d{3} \d{2} \d{2}',
      r'[8|\+7] \d{3} \d{3}-\d{2}-\d{2}'
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
    if isinstance(content, LoadException):
      return {
        'err': True
      }

    data = re.findall(r'<script type="text\/javascript">window\._sharedData =(.*);<\/script>', content)

    if len(data) == 0:
      return None

    try:
      instagram_data = json.loads(data[0])
      user_data = instagram_data.get('entry_data').get('ProfilePage')[0].get('graphql').get('user')
      biography = user_data.get('biography')
      ext_links = user_data.get('external_url')

    except:
      import traceback
      print(traceback.format_exc())
      return None

    return {
      'tel': self.get_telephone_from_page('{} {}'.format(biography, ext_links)),
      'links': ext_links
    }