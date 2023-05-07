#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui  by院长修改
# @Time : 2022/11/11 10:42
# cron "*/30 8-23 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('某营业厅直播抽奖');
# -------------------------------
"""
1. 脚本仅供学习交流使用, 请在下载后24h内删除
2. 环境变量说明:
   变量名(必须)：  TELECOM_PHONE_PASSWORD
   格式： 手机号&服务密码，1317xxx1322&123456
   单个CK塞多个账号时，以#分隔开：手机号&服务密码#手机号&服务密码，1317xxx1322&123456#1317xxx1322&123456
3. 必须登录过 电信营业厅 app的账号才能正常运行
"""
import re
from random import randint
from base64 import b64encode
from time import mktime, strptime, strftime, sleep as time_sleep
from requests import post, get, packages
packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"
from datetime import datetime, timedelta
from asyncio import wait, sleep, run

from tools.ql_api import get_cookie
from tools.tool import timestamp, get_environ, print_now
from tools.send_msg import push
from china_telecom import ChinaTelecom
import threading
import time
import requests
import json

from tools.notify import send

class TelecomLotter:
    def __init__(self, phone, password):
        self.phone = phone
        chinaTelecom = ChinaTelecom(phone, password)
        chinaTelecom.init()
        chinaTelecom.author()
        self.authorization = chinaTelecom.authorization
        self.ua = chinaTelecom.ua
        self.token = chinaTelecom.token

    def get_action_id(self, liveId):
        url = "https://appkefu.189.cn:8301/query/getWaresList"
        body = {
            "headerInfos": {
                "code": "getWaresList",
                "timestamp": datetime.now().__format__("%Y%m%d%H%M%S"),
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel128#samsung SM-G9860#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": self.token,
                "userLoginName": self.phone
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "limit": "",
                    "page": "1",
                    "liveId": liveId
                }
            }
        }
        headers = {
            "User-Agent": self.ua,
            "authorization": self.authorization
        }
        data = post(url, headers=headers, json=body).json()
        try:
            for waresInfo in data["responseData"]["data"]["waresInfos"]:
                print(waresInfo["title"])
                if "转盘" in waresInfo["title"] or "抽奖" in waresInfo["title"]:
                    active_code = findall(r"active_code\u003d(.*?)\u0026", waresInfo["link"])[0]
                    return active_code
            return None
        except:
            return None
    def get_action_id_other(self, liveId):
        def encrypt_phone():
            result = ""
            for i in self.phone:
                result += chr(ord(i) + 2)
            return result
        url = "https://wapmkt.189.cn:8301/query/directSeedingInfo"
        body = {
            "headerInfos": {
                "code": "directSeedingInfo",
                "timestamp": datetime.now().__format__("%Y%m%d%H%M%S"),
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel128#samsung SM-G9860#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": self.token,
                "userLoginName": self.phone
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "liveId": liveId,
                    "account": encrypt_phone()
                }
            }
        }
        headers = {
            "User-Agent": self.ua,
            "authorization": self.authorization
        }
        data = post(url, headers=headers, json=body).json()["responseData"]["data"]
        try:
            if data["buoyLink"] is None:
                return None
            active_code = findall(r"active_code\u003d(.*?)\u0026", data["buoyLink"])[0]
            return active_code
        except:
            return None
    async def lotter(self, liveId, period):
        """
        :param liveId: 直播间id
        :param period: 某个参数 暂不明意义 查询直播间信息时会返回
        :return:
        """
        print_now(f"当前执行的直播间id为{liveId}")
        for i in range(2):
            # active_code1 查询直播间购物车中的大转盘活动id
            active_code1 = self.get_action_id(liveId)
            # active_code2 查询直播间非购物车 而是右上角的大转盘活动id
            active_code2 = self.get_action_id_other(liveId)
            if active_code1 is not None or active_code2 is not None:
                break
            print(f"此直播间暂无抽奖活动, 等待10秒后再次查询 剩余查询次数{2 - i}")
            await sleep(10)
            continue
        if active_code1 is None and active_code2 is None:
            print("查询结束 本直播间暂无抽奖活动")
            return
        elif active_code1 is None or active_code2 is None:
            active_code = active_code1 if active_code2 is None else active_code2
            active_code_list = [active_code]
        else:
            active_code_list = [active_code1, active_code2]
        for active_code in active_code_list:
            url = "https://xbk.189.cn/xbkapi/active/v2/lottery/do"
            body = {
                "active_code": active_code,
                "liveId": liveId,
                "period": period
            }
            headers = {
                "User-Agent": self.ua,
                "authorization": self.authorization
            }
            data = post(url, headers=headers, json=body).json()
            print(data)
            time_sleep(10)
            if data["code"] == 0:
                push("直播抽奖", f"{self.phone}: 获得了{data['data']['title']}")
    def find_price(self):
        url = "https://xbk.189.cn/xbkapi/active/v2/lottery/getMyWinList?page=1&give_status=200&activeCode="
        headers = {
            "User-Agent": self.ua,
            "authorization": self.authorization
        }
        data = get(url, headers=headers).json()
        if data["code"] == 0:
            all_price_list = data["data"]
            compare_date = lambda date: date.split("-")[1] == str((datetime.now() + timedelta(hours=8 - int(strftime("%z")[2]))).month)
            month_price = [f'{info["win_time"]}: {info["title"]}' for info in all_price_list if compare_date(info["win_time"])]
            month_price_info = "\n".join(month_price)
            print(month_price_info)
            push("本月直播奖品查询", f"{self.phone}:\n{month_price_info}")
        else:
            print(f"获取奖品信息失败, 接口返回" + str(data))




def get_data():
    print('正在加载今日直播数据ing...')  
    all_list = []
    code = 1
    msg_str = ""
    for i in range(35):
        if code < 10:
            code_str = '0' + str(code)
        else:
            code_str = str(code)
        url = f'https://xbk.189.cn/xbkapi/lteration/index/recommend/anchorRecommend?provinceCode={code_str}'
        random_phone = f"1537266{randint(1000, 9999)}"
        headers = {
            "referer": "https://xbk.189.cn/xbk/newHome?version=9.4.0&yjz=no&l=card&longitude=%24longitude%24&latitude=%24latitude%24&utm_ch=hg_app&utm_sch=hg_sh_shdbcdl&utm_as=xbk_tj&loginType=1",
            "user-agent": f"CtClient;9.6.1;Android;12;SM-G9860;{b64encode(random_phone[5:11].encode()).decode().strip('=+')}!#!{b64encode(random_phone[0:5].encode()).decode().strip('=+')}"
        }
        # print(url)
        data = requests.get(url, headers=headers).json()
        body = data["data"]
        for i in body:
            if time.strftime('%Y-%m-%d') in i['start_time']:
                if i not in all_list:              
                    print('今日开播时间：'+i['start_time']+' 直播间名称：'+i['nickname'] ) 
                    print('安卓浏览器(如via、alook浏览器)直接打开链接  ctclient://startapp/android/open?LinkType=5&Link=https://xbk.189.cn/xbk/livingRoom?liveId='+str(i['liveId']) ) 
                    print('通用打开方式，先登录：https://xbk.189.cn/xbk/newHome  然后直接打开  https://xbk.189.cn/xbk/livingRoom?liveId='+str(i['liveId']) ) 
                    print('\n\n')
                    msg_str += '今日开播时间：'+i['start_time']+' 直播间名称：'+i['nickname']+'\n1、安卓打开方式\n浏览器(如via、alook浏览器)直接打开链接：\nctclient://startapp/android/open?LinkType=5&Link=https://xbk.189.cn/xbk/livingRoom?liveId='+str(i['liveId'])+'\n2、通用打开方式\n先登录：\nhttps://xbk.189.cn/xbk/newHome\n然后直接打开链接：\nhttps://xbk.189.cn/xbk/livingRoom?liveId='+str(i['liveId'])+'\n\n'
                    all_list.append(i)
        code += 1
    list = {}
    f = 1
    for i in all_list:
        list['liveRoom' + str(f)] = i
        f += 1
    print('直播数据加载完毕')
    print('\n\n')
    #发送消息
    send('电信星播客直播通知', msg_str)
    return list





def main(phone, password):
    apiType = 1
    #切换使用直接加载方式
    data = getData
    # try:
    #     url = "https://gitee.com/kele2233/genxin/raw/master/telecomLiveInfo.json"
    #     data = get(url, timeout=5).json()
    # except:
    #     print("主直播接口失效，进入备用抓包接口")
    #     data = list_d
    #     # try:
    #     #     url = "https://raw.githubusercontent.com/limoruirui/Hello-Wolrd/main/telecomLiveInfo.json"
    #     #     #url = "https://api.ruirui.fun/telecom/getLiveInfo"
    #     #     data = get(url, timeout=5).json()
    #     # except:
    #     #     url = "https://xbk.189.cn/xbkapi/lteration/index/recommend/anchorRecommend?provinceCode=01"
    #     #     random_phone = f"1537266{randint(1000, 9999)}"
    #     #     headers = {
    #     #         "referer": "https://xbk.189.cn/xbk/newHome?version=9.4.0&yjz=no&l=card&longitude=%24longitude%24&latitude=%24latitude%24&utm_ch=hg_app&utm_sch=hg_sh_shdbcdl&utm_as=xbk_tj&loginType=1",
    #     #         "user-agent": f"CtClient;9.6.1;Android;12;SM-G9860;{b64encode(random_phone[5:11].encode()).decode().strip('=+')}!#!{b64encode(random_phone[0:5].encode()).decode().strip('=+')}"
    #     #     }
    #     #     data = get(url, headers=headers).json()
    #     #     apiType = 2
    print(data)
    liveListInfo = {}
    allLiveInfo = data.values() if apiType == 1 else data["data"]
    for liveInfo in allLiveInfo:
        if 1740 > timestamp(True) - int(mktime(strptime(liveInfo["start_time"], "%Y-%m-%d %H:%M:%S"))) + (
                8 - int(strftime("%z")[2])) * 3600 > 0:
            liveListInfo[liveInfo["liveId"]] = liveInfo["period"]
    if len(liveListInfo) == 0:
        print("查询结束 没有近期开播的直播间")
    else:
        telecomLotter = TelecomLotter(phone, password)
        all_task = [telecomLotter.lotter(liveId, period) for liveId, period in liveListInfo.items()]
        run(wait(all_task))
    now = datetime.now()
    if now.hour == 12 + int(strftime("%z")[2]) and now.minute > 10:
        TelecomLotter(phone, password).find_price()
      


def start(phone,password):
    if phone == "" or password == "":
        print("未填写相应变量 退出")
        exit(0)
    main(phone, password)
    print("\n")




if __name__ == '__main__':
    getData = []
#    try:
#       url = "https://gitcode.net/weixin_52142858/telecomliveinfo/-/raw/master/telecomLiveInfo.json"
#       getData = get(url, timeout=5).json()
#    except:
#       #加载今日直播信息
#       print('主接口失效，使用备用接口中。。。。')  
#       getData=get_data()





    l = []
    getData=get_data()
    # user_map = []
    # cklist = get_cookie("TELECOM_PHONE_PASSWORD")
    # for i in range(len(cklist)):
    #     #以#分割开的ck
    #     split1 = cklist[i].split("#")
    #     if len(split1)>1:
    #         for j in range(len(split1)):
    #             split2 = split1[j].split("&")
    #             if len(split2)>1:
    #                 user_map.append(split1[j])
    #     else:
    #         userinfo = cklist[i].split("&")
    #         if len(userinfo)>1:
    #             user_map.append(cklist[i])



    # for i in range(len(user_map)):
    #     phone=""
    #     password=""
    #     userinfo = user_map[i].split("&")
    #     if len(userinfo)>1:
    #         phone = userinfo[0]
    #         password = userinfo[1]
    #     print('开始执行第{}个账号：{}'.format((i+1),phone))
    #     if phone == "" or password == "":
    #         print("当前账号未填写手机号或者密码 跳过")
    #         print("\n")
    #         continue
    #     p = threading.Thread(target=start,args=(phone,password))
    #     l.append(p)
    #     p.start()
    #     print("\n")
    # for i in l:
    #     i.join()
