from flask import Flask, render_template
from urllib.parse import quote
import requests
import json
import re
import asyncio
import aiohttp
import random

from my_asyncio import MyAsync

app = Flask(__name__)
app.debug = True

@app.route('/')
def main_page(name=None):
    return render_template('main.html', name=name)


def get_media_data(search_string):
    url = '''https://www.instagram.com/web/search/topsearch/?context=blended&query={}&rank_token=0.21158621296914282&include_reel=true'''.format(
        quote(search_string)
    )

    result = requests.get(url)
    return result

def get_user_info(user):
    url = '''https://www.instagram.com/{}/'''.format(
        user
    )
    print('get_url {}'.format(url))
    result = requests.get(url)
    content = result.content.decode('cp1251', errors='ignore')
    return {
        'tel': re.findall(r'\+7\d{6,}', content) or re.findall(r'[8|\+7]-\d+-\d+-\d+', content)
    }


async def async_get_user_info(user):
    url = '''https://www.instagram.com/{}/'''.format(
        user
    )
    print('get_url {}'.format(url))
    asyncio.sleep(random.randint(0, 10) * 1e-2)  # Чтобы инстраграмм нас не блокировал
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print('start_get_text {}'.format(url))
            content = await response.text()
            print('end_get_text {} {}'.format(url, content))
            return {
                'tel': re.findall(r'\+7\d{6,}', content) or
                       re.findall(r'[8|\+7]-\d+-\d+-\d+', content) or
                       re.findall(r'[8|\+7] \d{2,} \d{2,} \d{2,}', content)
            }


async def async_add_phone(container, user):
    result = await async_get_user_info(user)
    print(result)
    container[user] = result


@app.route('/page/<page>')
def get_page(page=None):
    data = []
    async_container = dict()
    err = ''
    content = get_media_data(page).content.decode('cp1251')
    try:
        res_json = json.loads(content)
        users = res_json.get('users')
        if users:
            for user in users:
                cu = user.get('user')
                user_name = cu.get('username')

                MyAsync.add_task(async_add_phone(async_container, user_name))

                # user_info = get_user_info(user_name)
                data.append({
                    'pos': cu.get('pk'),
                    'acc': user_name,
                    'name': cu.get('full_name'),
                    'fol': cu.get('follower_count'),
                    # 'tel': user_info.get('tel')
                })

            MyAsync.release()

    except:
        import traceback
        err = traceback.format_exc()

    data.sort(key=lambda i: i.get('fol'), reverse=True)
    
    print(async_container)
    if async_container:
        for user in data:
            user['tel'] = set(async_container.get(user.get('acc')).get('tel')) if user and user.get('acc') else ''

    return render_template('main.html', data=data, err=err, add_info='')

app.run(debug=True)