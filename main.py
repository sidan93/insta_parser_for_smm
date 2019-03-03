from flask import Flask, render_template
from urllib.parse import quote
import requests
import json
import re
import asyncio
import aiohttp
import random

from my_asyncio import MyAsync
from my_instagram import Instagram

app = Flask(__name__)
app.debug = True

inst = Instagram(token='0.21158621296914282', debug=True)

@app.route('/')
def main_page(name=None):
    return render_template('main.html', name=name)


async def async_add_phone(container, user_name):
    result = await inst.get_user_async(user_name)
    print(result)
    container[user_name] = result


@app.route('/page/<page>')
def get_page(page=None):
    data = []
    async_container = dict()
    err = ''
    content = inst.search(page)
    try:
        res_json = json.loads(content)
        users = res_json.get('users')
        
        async_loop = MyAsync()

        if users:
            for key, user in enumerate(users):
                cu = user.get('user')
                user_name = cu.get('username')

                async_loop.add_task(async_add_phone(async_container, user_name))

                data.append({
                    'pos': cu.get('pk'),
                    'acc': user_name,
                    'name': cu.get('full_name'),
                    'fol': cu.get('follower_count'),
                })

            async_loop.release()

    except:
        import traceback
        err = traceback.format_exc()

    data.sort(key=lambda i: i.get('fol'), reverse=True)
    for key, d in enumerate(data):
        d['key'] = key + 1
    
    print(async_container)
    if async_container:
        for user in data:
            user['tel'] = set(async_container.get(user.get('acc')).get('tel')) if user and user.get('acc') else ''

    return render_template('main.html', data=data, err=err, add_info='')

app.run(debug=True)