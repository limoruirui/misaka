"""
@yuanter 院长出品，仅供学习交流，请在下载后的24小时内完全删除 请勿将任何内容用于商业或非法目的，否则后果自负。
今日越城监控兑换_v0.3 监控1、话费油卡类2、电影票3、实物类
cron "0 0-59/5 * * * *" script-path=xxx.py,tag=匹配cron用
const $ = new Env('今日越城监控兑换商品');

功能：今日越城监控并兑换商品，可兑换列表：话费油卡类、电影票、实物类

若是监控了油卡和手机号类，请填写下列两个变量
环境变量jryc_monitor_youkaNumber  选填 油卡账号
环境变量jryc_monitor_mobileNumber  选填 手机账号

环境变量jryc_monitor_data  必填（短链接和长链接，二选一） 多账号直接新建多变量环境，也使用@或者#拼接
新增可选参数：指定兑换商品ID，当指定兑换商品ID存在时，请设置监控对应的商品类，如监控实物类
存在指定兑换商品ID时，可指定多个id，使用英文加号+拼接，如8928+8439+8430+8433

短链接，全部监控话费油卡类、电影票、实物类
格式 AccountId&SessionId&Sign&兑换积分&指定兑换商品ID
栗子，如637c7681b72ed364&64bcb6487d0506918&96d90a848f891afdc2bcd6cf&3000
或者637c7681b72ed364&64bcb6487d0506918&96d90a848f891afdc2bcd6cf&3000&8928+8439+8430+8433


长链接，可自定义监控某一类的商品，不需要监控的参数设置为False，监控顺序1、话费油卡类2、电影票3、实物类
格式 AccountId&SessionId&Sign&兑换积分&监控话费油卡类&监控电影票&监控实物类&指定兑换商品ID
栗子，如637c7681b7d2ed364&64bcb6487dee0506918&96da848f891afdc2bcd6cf&3000&True&True&True
或者637c7681b7d2ed364&64bcb6487dee0506918&96da848f891afdc2bcd6cf&3000&True&True&True&8928

解释
抓包 https://promoa.ejiaofei.cn/ShaoXingLogin/VerifyUser 取出body下三个参数，AccountId，SessionId，Sign
监控话费油卡类，默认True监控兑换 填True 或者 False
监控电影票，默认True监控兑换 填True 或者 False
监控实物类，默认True监控兑换 填True 或者 False
兑换积分，当商品满足兑换积分时，有库存且个人账户积分足够，则开始自动兑换
指定兑换商品ID，当指定兑换商品ID存在时，请设置监控对应的商品类，如监控实物类。可先执行一遍全部监控，即可根据任务日志找到商品ID

"""

##################################################自定义参数区域##################################################

range_num = 3000  # 默认低于3000积分不兑换
key = ""  # 企业微信推送 webhook 后面的 key
PUSH_PLUS_TOKEN = ''  #推送token
PUSH_PLUS_GROUP = '' #推送的群组
debug = False  # False  True
jryc_monitor_youkaNumber = "" # 油卡账号
jryc_monitor_mobileNumber = "" # 手机账号

##################################################源码区域，非维护勿动##################################################
import json
import re
import requests
from sys import stdout
import json, os
import datetime
import time
import threading


now = datetime.datetime.now()
hour = now.hour
minute = now.minute
# print("当前时间为：{}时{}分".format(hour, minute))
start_time = f'{hour}:{minute}:59.83'
# 场次时间
changci  = '10:00:00'


# 场次时间
if minute == 59:
    changci  = f'{hour+1}:00:00'
else:
    changci  = f'{hour}:{minute+1}:00'
changci  = datetime.datetime.strptime(str(datetime.datetime.now() + datetime.timedelta(days=0))[0:11] + changci, '%Y-%m-%d %H:%M:%S')
title = f'【今日越城监控商品】-----监控时间：{changci}'
# ck
ck_list = []
message = ""


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
def get_cookie(key, default=[], output=True):
    def no_read():
        if output:
            print_now(f"未填写环境变量 {key} 请添加")
        return default
    data = get_cookie_data(key)
    return data if data else no_read()

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


#push推送
def push_plus_bot(title, content):
    try:
        print_now("\n")
        if not PUSH_PLUS_TOKEN:
            print_now("PUSHPLUS服务的token未设置!!\n取消推送")
            return
        print_now("PUSHPLUS服务启动")
        url = 'http://pushplus.plus/send'
        data = {
            "token": PUSH_PLUS_TOKEN,
            "topic": PUSH_PLUS_GROUP,
            "title": title,
            "content": msg
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        if response['code'] == 200:
            print_now('推送成功！')
        else:
            print_now('推送失败！')
            print_now(response)

    except Exception as e:
        print_now(e)


# 企业微信推送
def weixin_hook(title: str, content: str) -> None:
    """
    通过 企业微信机器人 推送消息。
    """
    if not key:
        print("企业微信机器人 服务的 QYWX_KEY 未设置!!\n取消推送")
        return
    print("企业微信机器人服务启动")

    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=15
    ).json()

    if response["errcode"] == 0:
        print("企业微信机器人推送成功！")
    else:
        print("企业微信机器人推送失败！")


def main(count,value,remarks):
    print_now(f"===========开始执行任务，第{count}个账号，备注【{remarks}】===========\n")
    huafei = True # 话费油卡类，默认True监控兑换 填True 或者 False
    dianying = True # 电影票，默认True监控兑换 填True 或者 False
    shiwu = True # 实物类，默认True监控兑换 填True 或者 False
    ck = value.split("&")
    AccountId,SessionId,Sign = ck[0],ck[1],ck[2]
    # 兑换积分
    if len(ck) == 4:
        range_num = int(ck[3])
    assign = []
    # 指定兑换ID
    if len(ck) == 5:
        range_num = int(ck[3])
        id_list = ck[4].split("+")
        for i in range(len(id_list)):
            assign.append(int(id_list[i]))
        print_now(f"===========第{count}个账号，备注【{remarks}】，已设置指定兑换ID：{assign} 下面执行兑换指定的商品===========\n")
    if len(ck) >= 7:
        if len(ck) == 8:
            # 指定兑换ID
            id_list = ck[7].split("+")
            for i in range(len(id_list)):
                print_now(f"打印数据：{id_list[i]}")
                assign.append(int(id_list[i]))
            print_now(f"===========第{count}个账号，备注【{remarks}】，已设置指定兑换ID：{assign} 下面执行兑换指定的商品===========\n")
        range_num = int(ck[3])
        huafei_temp = ck[4]
        if huafei_temp is None or huafei_temp == "":
            huafei_temp = "True"
        if huafei_temp == "False":
            huafei = False

        dianying_temp = ck[5]
        if dianying_temp is None or dianying_temp == "":
            dianying_temp = "True"
        if dianying_temp == "False":
            dianying = False

        shiwu_temp = ck[6]
        if shiwu_temp is None or shiwu_temp == "":
            shiwu_temp = "True"
        if shiwu_temp == "False":
            shiwu = False
    if not AccountId or not SessionId or not Sign:
        print_now(f"===========第{count}个账号，备注【{remarks}】，参数不完整，程序未运行。请检查参数是否为空===========\n")
    else:
        url = "https://promoa.ejiaofei.cn/ShaoXingLogin/VerifyUser"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; PFGM00 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36;xsb_yuecheng;xsb_yuecheng;1.3.0;native_app'
        }

        payload = {
            "AccountId": AccountId,
            "SessionId": SessionId,
            "Sign": Sign

        }
        match = False
        try:
            response = requests.post(url, headers=headers, data=payload,timeout=60)
            value = response.json()["data"]
            # print(value)

            response = requests.post(url=value)
            html_code = response.text

            pattern = r'var SESSIONID = "(.*?)";'
            match = re.search(pattern, html_code)
        except Exception as ex:
            print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")} [{cookieKey["remarks"]}]登录出错了----------错误响应：\n{ex}')
        if match:
            SESSIONID = match.group(1)
            # print("SESSIONID:", SESSIONID)
            product_dict = {}
            takeId = 0
            rows = []
            url = 'https://jfwechat.chengquan.cn/integralMallUserProduct/getList'
            headers = {
                'uGRDXsIL': SESSIONID,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 11; PFGM00 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36;xsb_yuecheng;xsb_yuecheng;1.3.0;native_app',

            }
            # 查询用户总积分
            user_count_url = f'https://jfwechat.chengquan.cn/integralMallOrder/getIntegral'
            response = requests.post(user_count_url, headers=headers,timeout=60)
            user_count_data = response.json()
            user_count = user_count_data["data"]
            print_now(f"===========第{count}个账号，备注【{remarks}】，总积分：{user_count} ===========\n")

            # 话费油卡类
            if huafei:
                print_now(f"===========第{count}个账号，备注【{remarks}】，开始监控话费和油卡类===========")

                payload = {
                    "pageNumber": "1",
                    "pageSize": "10",
                    "userCategoryId": "1502",
                    "type": "PRODUCT_TEAM"
                }
                response = requests.post(url, headers=headers, data=payload)
                data = response.json()
                rows = data['data']['rows']

                for row in rows:
                    product_id = row['id']
                    product_name = row['productName']
                    consume_integral = row['consumeIntegral']
                    productType = row['productType']
                    # 跳过非指定的商品id
                    if product_id not in assign and len(assign) > 0:
                        if debug:
                            print_now(f'执行监控ID：{assign} 跳过非指定的商品id：{product_id}')
                        continue

                    product_dict[product_id] = {
                        'type': "huafei",
                        'Product Name': product_name,
                        'Product ID': product_id,
                        'Consume Integral': consume_integral,
                        'productType': productType,
                    }

            # 电影票
            if dianying:
                print_now(f"===========第{count}个账号，备注【{remarks}】，开始监控电影票类===========")

                payload = {
                    "pageNumber": "1",
                    "pageSize": "10",
                    "userCategoryId": "1501",
                    "type": "PRODUCT_TEAM",
                }
                response = requests.post(url, headers=headers, data=payload,timeout=60)
                data = response.json()
                rows = data['data']['rows']

                for row in rows:
                    product_id = row['id']
                    product_name = row['productName']
                    consume_integral = row['consumeIntegral']
                    productType = row['productType']
                    # 跳过非指定的商品id
                    if product_id not in assign and len(assign) > 0:
                        if debug:
                            print_now(f'执行监控ID：{assign} 跳过非指定的商品id：{product_id}')
                        continue

                    product_dict[product_id] = {
                        'type': "dianying",
                        'Product Name': product_name,
                        'Product ID': product_id,
                        'Consume Integral': consume_integral,
                        'productType': productType,
                    }

            # 实物类
            if shiwu:
                print_now(f"===========第{count}个账号，备注【{remarks}】，开始监控实物类===========")

                # 查询地址
                address_url = 'https://jfwechat.chengquan.cn/attribution/selectList'
                response = requests.post(address_url, headers=headers,timeout=60)
                address_data = response.json()
                address_list = address_data['data']
                if address_list is None or len(address_list)<1:
                    print_now(f"===========第{count}个账号，备注【{remarks}】，还未设置收货地址，请先设置地址。强制退出程序===========\n")
                    return
                # 默认使用第一个地址
                # print_now(f"地址：{address_list[0]}")
                takeId = address_list[0]["id"]

                payload = {
                    "pageNumber": "1",
                    "pageSize": "10",
                    "userCategoryId": "8388",
                    "type": "PRODUCT_MODULE"
                }
                response = requests.post(url, headers=headers, data=payload,timeout=60)
                data = response.json()
                rows = data['data']['rows']

                for row in rows:
                    product_id = row['id']
                    product_name = row['productName']
                    consume_integral = row['consumeIntegral']
                    # 跳过非指定的商品id
                    if product_id not in assign and len(assign) > 0:
                        if debug:
                            print_now(f'执行监控ID：{assign} 跳过非指定的商品id：{product_id}')
                        continue
                    product_dict[product_id] = {
                        'type': "shiwu",
                        'Product Name': product_name,
                        'Product ID': product_id,
                        'Consume Integral': consume_integral
                    }
            # 开始兑换
            exchange(SESSIONID,product_dict,takeId,remarks,range_num)


        else:
            print_now("No value found for SESSIONID")

# 开始兑换
def exchange(SESSIONID,product_dict,takeId,remarks,range_num):
    global message
    msg = ""
    headers = {
        'uGRDXsIL': SESSIONID,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; PFGM00 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36;xsb_yuecheng;xsb_yuecheng;1.3.0;native_app',

    }

    for product_id in product_dict:
        product_info = product_dict[product_id]
        data = {
            'productId': str(product_id),
            'propertyList': ''
        }
        # 实体类
        if product_info['type'] == "shiwu":
            monitor_url = 'https://jfwechat.chengquan.cn/integralMallProduct/getInventory'
            headers['Referer'] = f'https://jfwechat.chengquan.cn/integralMall/entityProductDetail?productId={str(product_id)}'
            response = requests.post(monitor_url, headers=headers, data=data,timeout=60)
            data = response.json()
            rows = data['data']
            for row in rows:
                saleable_inventory = row['saleableInventory']
                print_now(f"ID:[{product_info['Product ID']}] {product_info['Product Name']}")
                print_now(f"兑换积分:[{product_info['Consume Integral']}]库存:[{saleable_inventory}]\n")
                if saleable_inventory == 0:
                    # 库存为0，继续下一个商品
                    continue
                else:
                    if product_info['Consume Integral'] >= range_num:
                        headers['Referer'] = f'https://jfwechat.chengquan.cn/integralMall/entityProductDetail?productId={product_info["Product ID"]}'
                        # 兑换实体类
                        exchange_url = "https://jfwechat.chengquan.cn/integralMallOrder/entityOrderNow"
                        payload = {
                            'productId': product_info['Product ID'],
                            'exchangeNum': '1',
                            'takeId': takeId,
                            'propertyIdList': '',
                            'propertyList': '[]'
                        }


                        response = requests.post(exchange_url, headers=headers, data=payload,timeout=60)
                        # 处理返回的数据
                        print_now(response.text)
                        data = response.json()


                        # 需要推送的消息内容
                        msg = msg + f"ID:{product_info['Product ID']} {product_info['Product Name']}\n兑换积分:[{product_info['Consume Integral']}]库存:[{saleable_inventory}]\n{data}\n诺，上面兑换状态！\n\n"

                    else:
                        print_now(f"积分小于{range_num}不兑换")
                    # 防止并发出现频繁
                    time.sleep(0.5)
        # 话费类和电影票类
        if product_info['type'] == "huafei" or product_info['type'] == "dianying":
            monitor_url = 'https://jfwechat.chengquan.cn/integralMallOrder/checkInventory'
            headers['Referer'] = f'https://jfwechat.chengquan.cn/integralMall/productDetail?productId={str(product_id)}'
            response = requests.post(monitor_url, headers=headers, data=data)
            data = response.json()
            rows = data['data']
            # 库存
            saleable_inventory = rows['amount']
            # 虚拟类型
            productType = product_info['productType']
            print_now(f"ID:[{product_info['Product ID']}] {product_info['Product Name']}")
            print_now(f"兑换积分:[{product_info['Consume Integral']}]库存:[{saleable_inventory}]\n")
            if saleable_inventory == 0:
                # 库存为0，继续下一个商品
                continue
            # 兑换话费类和电影票类
            exchange_url = f'https://jfwechat.chengquan.cn/integralMallOrder/orderNow'
            headers['Referer'] = f'https://jfwechat.chengquan.cn/integralMall/productDetail?productId={product_info["Product ID"]}'
            # 判断账号是否需要填入
            rechargeNumber = ""
            # 加油卡账号||或者电影票账号
            if productType == "COUPON":
                rechargeNumber = jryc_monitor_youkaNumber
            # 手机号
            if productType == "RECHARGE":
                rechargeNumber = jryc_monitor_mobileNumber
            payload = {
                'productId': product_info['Product ID'],
                'exchangeNum': 1,
                'rechargeNumber': rechargeNumber,
                'exchangeAccount': ""
            }
            response = requests.post(exchange_url, headers=headers, data=payload,timeout=60)
            # 处理返回的数据
            print_now(response.text)
            data = response.json()
            errorMsg = data.get("errorMsg",None)
            if errorMsg is not None and (errorMsg.startswith("非商品兑换时间。请在周五 10:00-11:00内尝试。") or errorMsg.startswith("操作频繁，请稍后再试")):
                # 不执行添加消息操作，防止每次都添加该消息
                print_now(f'出现“非商品兑换时间。请在周五 10:00-11:00内尝试”或者“操作频繁，请稍后再试”，不执行添加消息操作\n')
                continue
            # 需要推送的消息内容
            msg = msg + f"ID:{product_info['Product ID']} {product_info['Product Name']}\n兑换积分:[{product_info['Consume Integral']}]库存:[{saleable_inventory}]\n{data}\n诺，上面兑换状态！\n\n"


    if msg != "":
        msg = f'<font color="red" style="font-size:24px;">用户“{remarks}”兑换状态如下：</font>\n' + msg
        message = message + msg + "\n\n"




if __name__ == '__main__':
    # 油卡账号
    jryc_monitor_youkaNumber_temp = get_cookie("jryc_monitor_youkaNumber")
    if jryc_monitor_youkaNumber_temp != "" and len(jryc_monitor_youkaNumber_temp)>0:
        jryc_monitor_youkaNumber = jryc_monitor_youkaNumber_temp[0]["value"]
    # 手机账号
    jryc_monitor_mobileNumber_temp = get_cookie("jryc_monitor_mobileNumber")
    if jryc_monitor_mobileNumber_temp != "" and len(jryc_monitor_mobileNumber_temp)>0:
        jryc_monitor_mobileNumber = jryc_monitor_mobileNumber_temp[0]["value"]
    l = []
    # 获取青龙CK和备注
    ck_list = []
    cklist = get_cookie("jryc_monitor_data")
    for i in range(len(cklist)):
        info = {}
        #多账号以#分割开的ck
        split1 = cklist[i]['value'].split("#")
        #多账号以@分割开的ck
        split2 = cklist[i]['value'].split("@")
        #多账号以换行\n分割开的ck
        split3 = cklist[i]['value'].split("\n")
        if len(split1)>1:
            for j in range(len(split1)):
                # 判断CK和兑换参数是否齐全
                split1_tmp = split1[j].split("&")
                if len(split1_tmp)>1:
                    info['value'] = split1[j]
                    info['remarks'] = cklist[i]['remarks']
                    ck_list.append(info)
        elif len(split2)>1:
            for j in range(len(split2)):
                # 判断CK和兑换参数是否齐全
                split2_tmp = split2[j].split("&")
                if len(split2_tmp)>1:
                    info['value'] = split2[j]
                    info['remarks'] = cklist[i]['remarks']
                    ck_list.append(info)
        elif len(split3)>1:
            for j in range(len(split3)):
                # 判断CK和兑换参数是否齐全
                split3_tmp = split3[j].split("&")
                if len(split3_tmp)>1:
                    info['value'] = split3[j]
                    info['remarks'] = cklist[i]['remarks']
                    ck_list.append(info)
        else:
            # 判断CK和兑换参数是否齐全
            userinfo = cklist[i]['value'].split("&")
            if len(userinfo)>1:
                ck_list.append(cklist[i])
    if len(ck_list)<1:
        print_now('未添加CK,退出程序~')
        exit(0)
    print_now(f'===========请注意，本脚本使用了异步线程方式，后续任务执行顺序看起来是错乱的，这是正常现象===========\n')
    print_now(f'===========本次一共找到 {len(ck_list)} 个账号===========\n')
    print_now(f'===========本次执行时间：{datetime.datetime.now().strftime("%H:%M:%S.%f")} 任务开始~===========\n')
    for j in range(len(ck_list)):
        ck = ck_list[j]["value"].split("&")
        remarks = ck_list[j]["remarks"]
        if len(ck)<3:
            print_now('===========第{j+1}个账号，CK参数不全，跳过===========\n')
            continue
        p = threading.Thread(target=main,args=(j+1,ck_list[j]["value"],remarks))
        l.append(p)
        p.start()
    for i in l:
        i.join()
    try:
        from notify import send
        send(title,message)
    except Exception as e:
        try:
            from tools.notify import send
            send(title,message)
        except Exception as e:
            try:
                push_plus_bot(title, message)
            except Exception as e:
                try:
                    weixin_hook(title, message)
                except Exception as e:
                    print_now(f'推送异常：{e}')
    print_now(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")} 任务结束~')
