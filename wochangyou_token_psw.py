#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@yuanter https://github.com/yuanter  by院长
# @Time : 2023/9/6 16:45
# cron "3 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('沃畅游密码登录');
# -------------------------------

"""
沃畅游密码登录 获取access_token环境并自动新增或者更新青龙环境
青龙环境变量：WoChangYouCK_PSW 手机号码&密码  账号和密码分别是联通app的账号和密码





"""
import requests,re
import json, os, random
import time
from datetime import datetime
from sys import stdout
import base64
from base64 import b64encode
from uuid import uuid4
from urllib.parse import quote
try:
    from Crypto.PublicKey.RSA import importKey, construct
    from Crypto.Cipher import PKCS1_v1_5
except:
    print("检测到还未安装 pycryptodome 依赖，请安装")
    print("如果安装依赖pycryptodome出错时，请先在linux中安装gcc、python3-dev、libc-dev三个依赖")
    exit(0)


# wxpusher消息推送
def wxpusher(title: str, content: str) -> None:
    """
    使用微信的wxpusher推送
    """
    if not WXPUSHER_TOKEN or not WXPUSHER_TOPIC_ID:
        print("wxpusher 服务的 token 或者 topicId 未设置!!\n取消推送")
        return
    print("wxpusher 服务启动")

    url = f"https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    contentType = 2
    if not WXPUSHER_CONTENT_TYPE:
        contentType = 2
    else:
        contentType = WXPUSHER_CONTENT_TYPE
    if contentType == 2:
        content = content.replace("\n", "<br/>")
    data = {
        "appToken":f"{WXPUSHER_TOKEN}",
        "content":f"{content}",
        "summary":f"{title}",
        "contentType":contentType,
        "topicIds":[
            f'{WXPUSHER_TOPIC_ID}'
        ],
        "verifyPay":False
    }
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=15
    ).json()

    if response["code"] == 1000:
        print("wxpusher推送成功！")
    else:
        print("wxpusher推送失败！")


ql_auth_path = '/ql/data/config/auth.json'
ql_config_path = '/ql/data/config/config.sh'
#判断环境变量
flag = 'new'
if not os.path.exists(ql_auth_path):
    ql_auth_path = '/ql/config/auth.json'
    ql_config_path = '/ql/config/config.sh'
    if not os.path.exists(ql_config_path):
        ql_config_path = '/ql/config/config.js'
    flag = 'old'
# ql_auth_path = r'D:\Docker\ql\config\auth.json'
ql_url = 'http://localhost:5600'


def __get_token() -> str or None:
    with open(ql_auth_path, 'r', encoding='utf-8') as f:
        j_data = json.load(f)
    return j_data.get('token')


def __get__headers() -> dict:
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=UTF-8',
        'Authorization': 'Bearer ' + __get_token()
    }
    return headers

# 封装读取环境变量的方法
def get_cookie(key, default="", output=True):
    def no_read():
        if output:
            print_now(f"未填写环境变量 {key} 请添加")
        return default
    return get_cookie_data(key) if get_cookie_data(key) else no_read()

#获取ck
def get_cookie_data(name):
    ck_list = []
    remarks_list = []
    cookie = None
    cookies = get_config_and_envs(name)
    for ck in cookies:
        data_temp = {}
        if ck["name"] != name:
            continue
        if ck.get('status') == 0:
            # ck_list.append(ck.get('value'))
            # 直接添加CK
            ck_list.append(ck)
    if len(ck_list) < 1:
        print('变量{}共配置{}条CK,请添加环境变量,或查看环境变量状态'.format(name,len(ck_list)))
    return ck_list

# 修改print方法 避免某些环境下python执行print 不会去刷新缓存区导致信息第一时间不及时输出
def print_now(content):
    print(content)
    stdout.flush()


# 查询环境变量
def get_envs(name: str = None) -> list:
    params = {
        't': int(time.time() * 1000)
    }
    if name is not None:
        params['searchValue'] = name
    res = requests.get(ql_url + '/api/envs', headers=__get__headers(), params=params)
    j_data = res.json()
    if j_data['code'] == 200:
        return j_data['data']
    return []


# 查询环境变量+config.sh变量
def get_config_and_envs(name: str = None) -> list:
    params = {
        't': int(time.time() * 1000)
    }
    #返回的数据data
    data = []
    if name is not None:
        params['searchValue'] = name
    res = requests.get(ql_url + '/api/envs', headers=__get__headers(), params=params)
    j_data = res.json()
    if j_data['code'] == 200:
        data = j_data['data']
    with open(ql_config_path, 'r', encoding='utf-8') as f:
        while  True:
            # Get next line from file
            line  =  f.readline()
            # If line is empty then end of file reached
            if  not  line  :
                break;
            #print(line.strip())
            exportinfo = line.strip().replace("\"","").replace("\'","")
            #去除注释#行
            rm_str_list = re.findall(r'^#(.+?)', exportinfo,re.DOTALL)
            #print('rm_str_list数据：{}'.format(rm_str_list))
            exportinfolist = []
            if len(rm_str_list) == 1:
                exportinfo = ""
            #list_all = re.findall(r'export[ ](.+?)', exportinfo,re.DOTALL)
            #print('exportinfo数据：{}'.format(exportinfo))
            #以export分隔，字符前面新增标记作为数组0，数组1为后面需要的数据
            list_all = ("标记"+exportinfo.replace(" ","").replace(" ","")).split("export")
            #print('list_all数据：{}'.format(list_all))
            if len(list_all) > 1:
                #以=分割，查找需要的环境名字
                tmp = list_all[1].split("=")
                if len(tmp) > 1:

                    info = tmp[0]
                    if name in info:
                        #print('需要查询的环境数据：{}'.format(tmp))
                        data_tmp = []
                        data_json = {
                            'id': None,
                            'value': tmp[1],
                            'status': 0,
                            'name': name,
                            'remarks': "",
                            'position': None,
                            'timestamp': int(time.time()*1000),
                            'created': int(time.time()*1000)
                        }
                        if flag == 'old':
                            data_json = {
                                '_id': None,
                                'value': tmp[1],
                                'status': 0,
                                'name': name,
                                'remarks': "",
                                'position': None,
                                'timestamp': int(time.time()*1000),
                                'created': int(time.time()*1000)
                            }
                        #print('需要的数据：{}'.format(data_json))
                        data.append(data_json)
        #print('第二次配置数据：{}'.format(data))
    return data


# 新增环境变量
def post_envs(name: str, value: str, remarks: str = None) -> list:
    params = {
        't': int(time.time() * 1000)
    }
    data = [{
        'name': name,
        'value': value
    }]
    if remarks is not None:
        data[0]['remarks'] = remarks
    res = requests.post(ql_url + '/api/envs', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return j_data['data']
    return []


# 修改环境变量
def put_envs(_id: str, name: str, value: str, remarks: str = None) -> bool:
    params = {
        't': int(time.time() * 1000)
    }

    data = {
        'name': name,
        'value': value,
        'id': _id
    }
    if flag == 'old':
        data = {
            'name': name,
            'value': value,
            '_id': _id
        }

    if remarks is not None:
        data['remarks'] = remarks
    res = requests.put(ql_url + '/api/envs', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False


# 禁用环境变量
def disable_env(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/envs/disable', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False


# 启用环境变量
def enable_env(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.put(ql_url + '/api/envs/enable', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False

# 删除环境变量
def delete_env(_id: str) -> bool:
    params = {
        't': int(time.time() * 1000)
    }
    data = [_id]
    res = requests.delete(ql_url + '/api/envs', headers=__get__headers(), params=params, json=data)
    j_data = res.json()
    if j_data['code'] == 200:
        return True
    return False




def base64_encode(data):
    message_bytes = data.encode('utf-8')  # 将字符串转换为字节型
    base64_data = base64.b64encode(message_bytes)  #进行加密
    # base64_data = base64.b64encode(data)  # 进行加密
    # print(base64_data,type(base64_data),len(base64_data))
    base64_data = base64_data.decode('utf-8')
    return base64_data

def base64_decode(data):
    #base64_bytes = data.encode('utf-8')
    message_bytes = base64.b64decode(data)
    message = message_bytes.decode('utf-8')
    return message


class RSA_Encrypt:
    def __init__(self, key):
        if isinstance(key, str):
            # 若提供的rsa公钥不为pem格式 则先将hex转化为pem格式
            # self.key = bytes.fromhex(key) if "PUBLIC KEY" not in key else key.encode()
            self.key = self.public_key(key) if "PUBLIC KEY" not in key else key.encode()
        else:
            print("提供的公钥格式不正确")

    def public_key(self, rsaExponent, rsaModulus=10001):
        e = int(rsaExponent, 16)
        n = int(rsaModulus, 16)  # snipped for brevity
        pubkey = construct((n, e)).export_key()
        return pubkey

    def encrypt(self, data, b64=False):
        data = data.encode('utf-8')
        length = len(data)
        default_length = 117
        pub_key = importKey(self.key)
        cipher = PKCS1_v1_5.new(pub_key)
        if length < default_length:
            rsa_text = cipher.encrypt(data)
            return b64encode(rsa_text).decode() if b64 else rsa_text.hex()
        offset = 0
        res = []
        while length - offset > 0:
            if length - offset > default_length:
                res.append(cipher.encrypt(data[offset:offset + default_length]))
            else:
                res.append(cipher.encrypt(data[offset:]))
            offset += default_length
        byte_data = b''.join(res)
        return b64encode(byte_data).decode() if b64 else byte_data.hex()



class UnicomLogin:
    def __init__(self, phone: str, password: str):
        self.rsa_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDc+CZK9bBA9IU+gZUOc6FUGu7y\nO9WpTNB0PzmgFBh96Mg1WrovD1oqZ+eIF4LjvxKXGOdI79JRdve9NPhQo07+uqGQ\ngE4imwNnRx7PFtCRryiIEcUoavuNtuRVoBAm6qdB0SrctgaqGfLgKvZHOnwTjyNq\njBUxzMeQlEC2czEMSwIDAQAB\n-----END PUBLIC KEY-----"
        self.phone_num = phone.rstrip("\n")
        self.password = password.rstrip("\n")
        self.deviceId = uuid4().hex
        self.appid = str(random.randint(0, 10))+"f"+str(random.randint(0, 10))+"af"+str(random.randint(0, 10))+"2ad6912d306b5053abf90c7ebbb695887bc870ae0706d573c348539c26c5c0a878641fcc0d3e90acb9be1e6ef858a59af546f3c826988332376b7d18c8ea2398ee3a9c3db947e2471d32a49612"

    def login_unicom(self):
        # print_now(self.phone_num+"---------"+self.password)
        headers = {
            'Host': 'm.client.10010.com',
            'Accept': '*/*',
            'User-Agent': 'ChinaUnicom.x CFNetwork iOS/15.0.1 unicom{version:iphone_c@10.0700}',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = f"isFirstInstall=1&simCount=1&yw_code=&deviceOS=android13&mobile={quote(RSA_Encrypt(self.rsa_key).encrypt(self.phone_num, b64=True))}&netWay=Wifi&version=android%4010.0100&deviceId={self.deviceId}&password={quote(RSA_Encrypt(self.rsa_key).encrypt(self.password, b64=True))}&keyVersion=&provinceChanel=general&appId={self.appid}&deviceModel=V1936A&androidId={uuid4().hex[8:24]}&deviceBrand=&timestamp={datetime.today().__format__('%Y%m%d%H%M%S')}"

        # data = {
        #     "version": "iphone_c@10.0700",
        #     "mobile": quote(RSA_Encrypt(self.rsa_key).encrypt(self.phone_num, b64=True)),
        #     "appId": self.appid,
        #     "deviceId": self.deviceId,
        #     "password": quote(RSA_Encrypt(self.rsa_key).encrypt(self.password, b64=True)),
        # }
        response = requests.post('https://m.client.10010.com/mobileService/login.htm', headers=headers,data=data)
        data = response.json()
        self.ecs_token = data.get("ecs_token")
        self.token_online = data.get("token_online")
        print_now(f'账号【{self.phone_num}】成功获取到【token_online】：{self.token_online}\n账号【{self.phone_num}】成功获取到【ecs_token】：{self.ecs_token}\n账号【{self.phone_num}】成功获取到【appid】：{self.appid}')
        return self.ecs_token


    def get_wo_speed_ticket(self):
        if self.ecs_token == "" or self.ecs_token is None:
            return ""
        
        cookies = {
            'ecs_token': self.ecs_token,
        }

        headers = {
            'Host': 'm.client.10010.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@10.0700}',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Referer': 'https://m.client.10010.com',
        }

        params = {
            'to_url': 'https://web.wostore.cn/web/flowGame/index.html?channelId=GAMELTAPP_90006',
        }

        response = requests.get(
            'https://m.client.10010.com/mobileService/openPlatform/openPlatLineNew.htm',
            params=params,
            cookies=cookies,
            headers=headers,
            allow_redirects=False
        )
        location = response.headers['Location']
        return location[location.find("ticket=") + len('ticket='):location.rfind("&versio")]


    def wo_speed_login(self):
        if self.ticket == "" or self.ticket is None:
            return ""
        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://web.wostore.cn',
            'Referer': 'https://web.wostore.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/109.0.0.0',
            'accept': 'application/json',
            'channelId': 'GAMELTAPP_90005',
            'device': '8',
            'rnVersion': '',
            'versionCode': '',
        }

        json_data = {
            'identityType': 'ticketToken',
            'code': self.ticket,
            'uuid': '3cc1b0ff-ddb4-49dc-9e87-4d51811f7ea1',
        }

        response = requests.post('https://game.wostore.cn/api/app/user/v2/login', headers=headers, json=json_data)
        d = response.json().get('data')
        return d.get('access_token')

    def deal_data(self):
        if self.ticket == "" or self.ticket is None:
            print_now(f'账号【{self.phone_num}】获取access_token失败\n')
            return ""
        try:
            print_now(f'账号【{self.phone_num}】成功获取到【access_token】：{self.access_token}\n请复制保存使用')
            # 获取沃畅游CK
            cklist_temp = get_cookie("WoChangYouCK")
            flag = False
            if len(cklist_temp)>0:
                for i in range(len(cklist_temp)):
                    ck_temp = cklist_temp[i]
                    if ck_temp["remarks"] == phone:
                        flag = True
                        print_now(f"账号【{self.phone_num}】自动更新access_token至青龙环境：WoChangYouCK  备注为：{phone}\n")
                        if flag == "old":
                            # print("进入旧版本青龙禁用方法")
                            put_envs(ck_temp["_id"], ck_temp['name'], self.access_token, phone)
                            # disable_env(ck_temp["_id"])
                            # delete_env(ck_temp["_id"])
                        elif flag == "new":
                            # print("进入新版本青龙禁用方法")
                            put_envs(ck_temp["id"], ck_temp['name'], self.access_token, phone)
                            # disable_env(ck_temp["id"])
                            # delete_env(ck_temp["id"])
            if not flag:
                print_now(f"账号【{self.phone_num}】自动新增access_token至青龙环境：WoChangYouCK  备注为：{phone}\n")
                post_envs("WoChangYouCK", self.access_token, phone)
        except Exception as e:
            print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{phone}】 登录失败，错误信息：{e}\n")


    def main(self):
        self.login_unicom()
        self.ticket = self.get_wo_speed_ticket()
        self.access_token = self.wo_speed_login()
        self.deal_data()


def start(phone,password):
    ul = UnicomLogin(phone,password)
    ul.main()

if __name__ == "__main__":
    l = []
    ck_list = []
    cklist = get_cookie("WoChangYouCK_PSW")
    for i in range(len(cklist)):
        info = {}
        #多账号以#分割开的ck
        split1 = cklist[i]['value'].split("#")
        #多账号以@分割开的ck
        split2 = cklist[i]['value'].split("@")
        #多账号以换行\n分割开的ck
        split3 = cklist[i]['value'].split("\n")
        remarks = cklist[i].get("remarks",None)
        if len(split1)>1:
            for j in range(len(split1)):
                info['value'] = split1[j]
                if remarks is None:
                    info['remarks'] = split1[j]
                else:
                    info['remarks'] = remarks
                ck_list.append(info)
        elif len(split2)>1:
            for j in range(len(split2)):
                info['value'] = split2[j]
                if remarks is None:
                    info['remarks'] = split2[j]
                else:
                    info['remarks'] = remarks
                ck_list.append(info)
        elif len(split3)>1:
            for j in range(len(split3)):
                info['value'] = split3[j]

                if remarks is None:
                    info['remarks'] = split3[j]
                else:
                    info['remarks'] = remarks
                ck_list.append(info)
        else:
            if remarks is None or remarks == "":
                cklist[i]['remarks'] = cklist[i]['value']
            ck_list.append(cklist[i])
    if len(ck_list)<1:
        print_now('未添加CK,退出程序~')
        exit(0)



    for i in range(len(ck_list)):
        ck = ck_list[i]
        data = ck.get("value",None)
        if data is None:
            print_now("当前账号未填写 跳过\n")
            continue
        tmp_list = data.split("&")
        if len(tmp_list)<2:
            print_now("参数不齐 跳过\n")
            continue
        phone = tmp_list[0]
        password = tmp_list[1]
        print_now(f'开始执行第 {i+1} 个账号：{phone}')
        start(phone,password)

