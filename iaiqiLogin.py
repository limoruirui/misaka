#留作备份
#扫码获取爱奇艺P00001, 此二维码有效期只有半分钟,但是爱奇艺没给二维码失效判断,所以默认执行6次后未完成扫码就结束
#实测此方法获取的P00001有效期为三个月,如果只用于签到和日常任务,超过三个月之后还能用,但是无法碰蛋和查询信息
from requests import post, get
from random import random
from hashlib import md5
from time import sleep
from os import remove
try:
    from PIL import image
except:
   print('您当前未安装pillow库'，请使用pip3 install pillow安装')
def getToken():
    url = 'https://passport.iqiyi.com/apis/qrcode/gen_login_token.action'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    data = {
        'agenttype': 1,
        'app_version': '',
        'device_id': '',
        'device_name': '网页端',
        'fromSDK': 1,
        'ptid': '01010021010000000000',
        'sdk_version': '1.0.0',
        'surl': 1
    }
    return post(url, headers=headers, data=data).json()['data']['token']
def qrcode(token):
    url = f'https://qrcode.iqiyipic.com/login/?data=https%3A%2F%2Fpassport.iqiyi.com%2Fapis%2Fqrcode%2Ftoken_login.action%3Ftoken%3D{token}&property=0&salt={md5Encode(f"35f4223bb8f6c8638dc91d94e9b16f5https%3A%2F%2Fpassport.iqiyi.com%2Fapis%2Fqrcode%2Ftoken_login.action%3Ftoken%3D{token}")}&width=162&_={random()}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    req = get(url, headers=headers)
    with open('登录二维码.png', 'wb') as f:
        f.write(req.content)
    image.open('登录二维码.png').show()
def login(token):
    url = 'https://passport.iqiyi.com/apis/qrcode/is_token_login.action'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }   
    data = {
        'agenttype': 1,
        'app_version': '',
        'device_id': '',
        'fromSDK': 1,
        'ptid': '01010021010000000000',
        'sdk_version': '1.0.0',
        'token': token
    }
    for i in range(6):
        req = post(url, headers=headers, data=data)
        code = req.json()['code']
        if code == 'A00000':
            cookie = f"您的P00001为{req.cookies.get('P00001')}"
            remove('登录二维码.png')
            return cookie
        else:
            sleep(8)
            continue
    remove('登录二维码.png')
    return '本次扫码未成功,可能是二维码失效或者未知原因'
def start():
    token = getToken()
    qrcode(token)
    print(login(token))
def md5Encode(str): 
	m = md5(str.encode(encoding='utf-8'))
	return m.hexdigest()
if __name__ == '__main__':
    start()
