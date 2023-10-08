#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@yuanter https://github.com/yuanter  by院长
# @Time : 2023/9/4 02:25
# cron "15 1 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('沃畅游破限速');
# -------------------------------

"""
说明：首次使用，联通app首页--5g新通信--联通畅游，点击个人中心，手动登录一遍
1. 沃畅游破限速 支持多账号执行 需要抓包沃畅游，找Authorization值 脚本仅供学习交流使用, 请在下载后24h内删除
2. cron说明 晚上12点01分15秒开始执行 可直接使用默认cron，亦可以自行修改
3. 环境变量说明:
    变量名(必须)： WoChangYouCK  格式： 抓包沃畅游Authorization，填入Authorization值即可
    单个CK塞多个账号时，以#或者@分隔开：CK1#CK2
注：本脚本可配合另外一个登录抓包脚本使用，自动填入CK

wxpusher推送(非必填)
青龙变量：WoChangYouCK_WXPUSHER_TOKEN   wxpusher推送的token
青龙变量：WoChangYouCK_WXPUSHER_TOPIC_ID   wxpusher推送的topicId(主题ID，非UID)
网址：https://wxpusher.zjiecode.com/admin/main/topics/list
"""
import requests,re, random
import json, os
import time
from sys import stdout




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



# WXPUSHER_TOKEN
WoChangYouCK_WXPUSHER_TOKEN_temp = get_cookie("WoChangYouCK_WXPUSHER_TOKEN")
if WoChangYouCK_WXPUSHER_TOKEN_temp != "" and len(WoChangYouCK_WXPUSHER_TOKEN_temp)>0:
    WXPUSHER_TOKEN = WoChangYouCK_WXPUSHER_TOKEN_temp[0]["value"]

# WXPUSHER_TOPIC_ID
WoChangYouCK_WXPUSHER_TOPIC_ID_temp = get_cookie("WoChangYouCK_WXPUSHER_TOPIC_ID")
if WoChangYouCK_WXPUSHER_TOPIC_ID_temp != "" and len(WoChangYouCK_WXPUSHER_TOPIC_ID_temp)>0:
    WXPUSHER_TOPIC_ID = WoChangYouCK_WXPUSHER_TOPIC_ID_temp[0]["value"]

msg = ""
isDebugger = False




def get_member_info(ck):
    authorization = ck["value"]
    remarks = ck["remarks"]
    headers = {
        'Host': 'game.wostore.cn',
        'Authorization': authorization,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/109.0.0.0',
        'Content-Type': 'application/json;charset=utf-8',
        'accept': 'application/json',
        'channelId': 'GAMELTAPP_90005',
        'device': '8',
        'Origin': 'https://web.wostore.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://web.wostore.cn/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }

    try:
        response = requests.get('https://game.wostore.cn/api/app/user/v3/getMemberInfo', headers=headers)
        # print(response.text)
        # print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】获取个人信息发送成功，响应：{response.json()}")
    except Exception as e:
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】获取个人信息发送失败，错误信息：{e}")



def send_speed_add(ck):
    global msg
    authorization = ck["value"]
    remarks = ck["remarks"]
    url = 'https://game.wostore.cn/api/app/user/qosSpeedUp/add'
    headers = {
        'authorization': authorization,
        'Content-Type': 'application/json;charset=utf-8',
        "versioncode": "4016",
        "channelid": "GAMELTJS_10001",
        "device": "1",
        "rnversion": "undefined",
        "Host": "game.wostore.cn",
        # "User-Agent": "okhttp/4.9.2",
        'User-Agent': 'ChinaUnicom.x CFNetwork iOS/15.0.1 unicom{version:iphone_c@10.0700}',
        "Accept-Encoding":"gzip"
    }
    data = {
        'firstTime': '00:00-23:30',
        'secondTime': '23:30-23:59'
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】重置加速时间，响应：{response.json()}")
        msg += f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】重置加速时间，响应：{response.json()}\n"
    except Exception as e:
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】 重置加速时间发送失败，错误信息：{e}")
        msg += f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】重置加速时间发送失败，错误信息：{e}\n"


def send_speed_start(ck):
    global msg
    authorization = ck["value"]
    remarks = ck["remarks"]
    headers = {
        'Host': 'game.wostore.cn',
        'channelid': 'GAMELTJS_10001',
        'Accept': 'application/json',
        'Authorization': authorization,
        'rnversion': 'undefined',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Content-Type': 'application/json;charset=utf-8',
        'versioncode': '4014',
        # 'User-Agent': 'GloudGame/68 CFNetwork/1312 Darwin/21.0.0',
        'User-Agent': 'ChinaUnicom.x CFNetwork iOS/15.0.1 unicom{version:iphone_c@10.0700}',
        'device': '2',
    }

    json_data = {
        'channelId': 'GAMELTJS_10001',
        'privateIp': '10.117.226.153',
    }

    try:
        response = requests.post('https://game.wostore.cn/api/app/user/v3/qos/start', headers=headers, json=json_data)
        # print(response.text)
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】立即加速，响应：{response.json()}")
        msg += f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】立即加速，响应：{response.json()}\n\n"
    except Exception as e:
        print_now(f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】加速发送失败，错误信息：{e}")
        msg += f"【{time.strftime('%Y-%m-%d %H:%M:%S')}】 ---- 【{remarks}】加速发送失败，错误信息：{e}\n\n"


if __name__ == "__main__":
    l = []
    ck_list = []
    cklist = get_cookie("WoChangYouCK")
    for i in range(len(cklist)):

        #多账号以#分割开的ck
        split1 = cklist[i]['value'].split("#")
        #多账号以@分割开的ck
        split2 = cklist[i]['value'].split("@")
        #多账号以换行\n分割开的ck
        split3 = cklist[i]['value'].split("\n")
        remarks = cklist[i].get("remarks",None)
        if len(split1)>1:
            for j in range(len(split1)):
                info = {}
                info['value'] = split1[j]
                if remarks is None:
                    info['remarks'] = split1[j]
                else:
                    info['remarks'] = remarks
                ck_list.append(info)
        elif len(split2)>1:
            for j in range(len(split2)):
                info = {}
                info['value'] = split2[j]
                if remarks is None:
                    info['remarks'] = split2[j]
                else:
                    info['remarks'] = remarks
                ck_list.append(info)
        elif len(split3)>1:
            for j in range(len(split3)):
                info = {}
                info['value'] = split3[j]
                if remarks is None:
                    info['remarks'] = split3[j]
                else:
                    info['remarks'] = remarks
                ck_list.append(info)
        else:
            if remarks is None:
                cklist[i]['remarks'] = cklist[i]['value']
            ck_list.append(cklist[i])
    if len(ck_list)<1:
        print_now('未添加CK,退出程序~')
        exit(0)



    for i in range(len(ck_list)):
        ck = ck_list[i]
        print_now(f'开始执行第 {i+1} 个账号')
        if ck is None:
            print_now("当前账号未填写 跳过\n")
            continue
        get_member_info(ck)
        send_speed_add(ck)
        send_speed_start(ck)
        #解决随机时间问题
        ran_time = random.randint(3, 5)
        if isDebugger == False and i != (len(ck_list)-1):
            print_now(f"随机休眠{ran_time}秒，执行下一个账号操作\n\n")
            time.sleep(ran_time)
        print_now("\n")

    print_now("提示：\n测试请在第二天凌晨12点30分后，使用5g信号再测试，部分地区4g不生效。\n“鉴权失败”只代表未开通联通加速会员(非必须开通)，非代表破限速失败，请自行测试\n\n")
    msg += f'提示：\n测试请在第二天凌晨12点30分后，使用5g信号再测试，部分地区4g不生效。\n“鉴权失败”只代表未开通联通加速会员(非必须开通)，非代表破限速失败，请自行测试\n\n'
    if WXPUSHER_TOKEN != "" and WXPUSHER_TOPIC_ID != "" and msg != "":
        wxpusher("沃畅游破限速",msg)
