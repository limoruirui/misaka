#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@yuanter https://github.com/yuanter  by院长
# @Time : 2023/9/6 18:25
# cron "1 1 1 1 1" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('沃畅游短信登录');
# -------------------------------

"""
沃畅游短信登录 获取access_token环境并自动新增或者更新青龙环境
青龙变量：WoChangYouCK_Phone 手机号码
青龙变量：WoChangYouCK_Code 验证码
wxpusher推送(非必填)
青龙变量：WoChangYouCK_WXPUSHER_TOKEN   wxpusher推送的token
青龙变量：WoChangYouCK_WXPUSHER_TOPIC_ID   wxpusher推送的topicId

步骤：
1. 先填写变量WoChangYouCK_Phone(手机号)，然后执行本脚本
2. 获取到验证码后，再填入变量WoChangYouCK_Code(验证码)，再次执行脚本

请注意：
变量WoChangYouCK_Code不存在时，会执行发送验证码操作
变量WoChangYouCK_Code存在时，会自动登录并生成青龙环境WoChangYouCK，同时会在青龙环境备注上手机号。或者自己根据日志自行复制access_token值

"""
import requests,re
import json, os
import time
from sys import stdout
import base64

WXPUSHER_TOKEN = '' # wxpusher推送的token
WXPUSHER_TOPIC_ID = '' # wxpusher推送的topicId
WXPUSHER_CONTENT_TYPE = 2  # wxpusher推送的样式，1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签)，默认为2
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
        print(f"wxpusher推送出错响应内容：{response}" )


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


# 修改环境变量1，青龙2.11.0以下版本（不含2.11.0）
def put_envs_old(_id: str, name: str, value: str, remarks: str = None) -> bool:
    params = {
        't': int(time.time() * 1000)
    }

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


# 修改环境变量2，青龙2.11.0以上版本（含2.11.0）
def put_envs_new(_id: int, name: str, value: str, remarks: str = None) -> bool:
    params = {
        't': int(time.time() * 1000)
    }

    data = {
        'name': name,
        'value': value,
        'id': _id
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



# WXPUSHER_TOKEN
WoChangYouCK_WXPUSHER_TOKEN_temp = get_cookie("WoChangYouCK_WXPUSHER_TOKEN")
if WoChangYouCK_WXPUSHER_TOKEN_temp != "" and len(WoChangYouCK_WXPUSHER_TOKEN_temp)>0:
    WXPUSHER_TOKEN = WoChangYouCK_WXPUSHER_TOKEN_temp[0]["value"]

# WXPUSHER_TOPIC_ID
WoChangYouCK_WXPUSHER_TOPIC_ID_temp = get_cookie("WoChangYouCK_WXPUSHER_TOPIC_ID")
if WoChangYouCK_WXPUSHER_TOPIC_ID_temp != "" and len(WoChangYouCK_WXPUSHER_TOPIC_ID_temp)>0:
    WXPUSHER_TOPIC_ID = WoChangYouCK_WXPUSHER_TOPIC_ID_temp[0]["value"]


phone = ""
msg = ""


def send_post(ck):
    phone = ck["value"]
    phone = base64_encode(phone)
    remarks = ck["remarks"]
    url = 'https://game.wostore.cn/api/app/user/v3/getVerificationCode'
    headers = {
        'authorization': '',
        'Content-Type': 'application/json;charset=utf-8',
        "versioncode": "4016",
        "channelid": "GAMELTJS_10001",
        "device": "1",
        "rnversion": "0",
        "Host": "game.wostore.cn",
        "User-Agent": "okhttp/4.9.2",
        "Accept-Encoding":"gzip"
    }
    data = {"phone":phone }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】 短信发送成功，响应：{response.json()}")
    except Exception as e:
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】 短信发送失败，错误信息：{e}")


def login_post(cookieKey):
    global phone
    global msg
    code = cookieKey["value"]
    code = base64_encode(code)
    new_phone = base64_encode(phone)
    url = 'https://game.wostore.cn/api/app/user/v3/login'
    headers = {
        'authorization': '',
        'Content-Type': 'application/json;charset=utf-8',
        "versioncode": "4016",
        "channelid": "GAMELTJS_10001",
        "device": "1",
        "rnversion": "0",
        "Host": "game.wostore.cn",
        "User-Agent": "okhttp/4.9.2",
        "Accept-Encoding":"gzip"
    }
    data = {"identityType":"phoneVerificationCode","identifier": new_phone,"code":code}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        text = response.json()
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{phone}】 登录成功，响应：{text}\n")
        if text["code"] == 200:
            data = text["data"]
            access_token = data["access_token"]
            print_now(f'成功获取access_token: {access_token}  请复制保存使用\n')
            # 获取沃畅游CK
            cklist_temp = get_cookie("WoChangYouCK")
            flag_temp = False
            if len(cklist_temp)>0:
                for i in range(len(cklist_temp)):
                    ck_temp = cklist_temp[i]
                    if ck_temp["remarks"] == phone:
                        flag_temp = True
                        put_flag = True
                        if flag == "old":
                            _id = ck_temp.get("_id",None)
                            if not _id:
                                _id = ck_temp["id"]
                                put_flag = put_envs_new(_id, ck_temp['name'], access_token, phone)
                            else:
                                put_flag = put_envs_old(_id, ck_temp['name'], access_token, phone)
                            # print("进入旧版本青龙禁用方法")
                            # disable_env(_id)
                            # delete_env(_id)
                        elif flag == "new":
                            put_flag = put_envs_new(ck_temp["id"], ck_temp['name'], access_token, phone)
                            # print("进入新版本青龙禁用方法")
                            # disable_env(ck_temp["id"])
                            # delete_env(ck_temp["id"])

                        if put_flag:
                            print_now(f"账号【{phone}】自动更新access_token至青龙环境：WoChangYouCK  备注为：{phone}")
                            msg += f"账号【{phone}】自动更新access_token至青龙环境：WoChangYouCK  备注为：{phone}\n\n"
                        else:
                            print_now(f"账号【{phone}】自动更新access_token至青龙环境：失败")
                            msg += f"账号【{phone}】自动更新access_token至青龙环境：失败\n\n"
            if not flag_temp:
                post_envs("WoChangYouCK", access_token, phone)
                print_now(f"账号【{phone}】自动新增access_token至青龙环境：WoChangYouCK  备注为：{phone}")
                msg += f"账号【{phone}】自动新增access_token至青龙环境：WoChangYouCK  备注为：{phone}\n\n"


    except Exception as e:
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{phone}】 登录失败，错误信息：{e}")
        msg += f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{phone}】 登录失败，错误信息：{e}\n\n"





# print_now(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 脚本已启动，默认每隔15分钟发送一次POST请求\n")

if __name__ == "__main__":
    l = []
    ck_list = []
    cklist = get_cookie("WoChangYouCK_Phone")
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
                    info['remarks'] = split1[j].split("&")[0]
                ck_list.append(info)
        elif len(split2)>1:
            for j in range(len(split2)):
                info['value'] = split2[j]
                if remarks is None:
                    info['remarks'] = split2[j]
                else:
                    info['remarks'] = split2[j].split("&")[0]
                ck_list.append(info)
        elif len(split3)>1:
            for j in range(len(split3)):
                info['value'] = split3[j]

                if remarks is None:
                    info['remarks'] = split3[j]
                else:
                    info['remarks'] = split3[j].split("&")[0]
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
        phone = ck.get("value",None)
        if phone is None:
            print_now("当前账号未填写 跳过\n")
            continue
        print_now(f'开始执行第 {i+1} 个账号：{phone}')
        code_list = get_cookie("WoChangYouCK_Code")
        if len(code_list)>0:
            login_post(code_list[0])
        else:
            send_post(ck)
    if WXPUSHER_TOKEN != "" and WXPUSHER_TOPIC_ID != "" and msg != "":
        wxpusher("沃畅游短信登录",msg)
