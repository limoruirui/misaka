#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui  by院长修改
# @Time : 2022/9/12 16:10
# cron "0 9,12 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('电信签到');
# -------------------------------

"""
1. 电信签到 支持多账号执行 不需要抓包 脚本仅供学习交流使用, 请在下载后24h内删除
2. cron说明 12点必须执行一次(用于兑换) 然后12点之外还需要执行一次(用于执行每日任务) 一天共两次 可直接使用默认cron
3. 环境变量说明:
    变量名(必须)：  TELECOM_PHONE_PASSWORD  格式： 手机号&服务密码，1317xxx1322&123456
    单个CK塞多个账号时，以#分隔开：手机号&服务密码#手机号&服务密码，1317xxx1322&123456#1317xxx1322&123456
    选填  TELECOM_FOOD  : 给宠物喂食次数 默认为0 不喂食 根据用户在网时长 每天可以喂食5-10次
4. 必须登录过 电信营业厅 app的账号才能正常运行
"""
"""
update:
    2022.10.25 参考大佬 github@QGCliveDavis https://github.com/QGCliveDavis 的 loginAuthCipherAsymmertric 参数解密 新增app登录获取token 完成星播客系列任务 感谢大佬
    2022.11.11 增加分享任务
"""
import re
from datetime import date, datetime
from random import shuffle, randint, choices
from time import sleep, strftime
from re import findall
from requests import get, post
from base64 import b64encode
from tools.aes_encrypt import AES_Ctypt
from tools.rsa_encrypt import RSA_Encrypt
from tools.tool import timestamp, get_environ, print_now
from tools.ql_api import get_cookie
from tools.send_msg import push
from tools.notify import send
from login.telecom_login import TelecomLogin
from string import ascii_letters, digits
import threading


msg_str = ""


class ChinaTelecom:
    def __init__(self, account, pwd, checkin=True):
        self.phone = account
        self.ticket = ""
        self.token = ""
        if pwd != "" and checkin:
            userLoginInfo = TelecomLogin(account, pwd).main()
            self.ticket = userLoginInfo[0]
            self.token = userLoginInfo[1]

    def init(self):
        self.msg = ""
        self.ua = f"CtClient;9.6.1;Android;12;SM-G9860;{b64encode(self.phone[5:11].encode()).decode().strip('=+')}!#!{b64encode(self.phone[0:5].encode()).decode().strip('=+')}"
        self.headers = {
            "Host": "wapside.189.cn:9001",
            "Referer": "https://wapside.189.cn:9001/resources/dist/signInActivity.html",
            "User-Agent": self.ua
        }
        self.key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6\nJGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65\ndU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORc\nAdcbpk2L+udld5kZNwIDAQAB\n-----END PUBLIC KEY-----"


    def req(self, url, method, data=None):
        if method == "GET":
            data = get(url, headers=self.headers).json()
            return data
        elif method.upper() == "POST":
            data = post(url, headers=self.headers, json=data).json()
            return data
        else:
            print_now("您当前使用的请求方式有误,请检查")

    # 长明文分段rsa加密
    def telecom_encrypt(self, text):
        if len(text) <= 32:
            return RSA_Encrypt(self.key).encrypt(text)
        else:
            encrypt_text = ""
            for i in range(int(len(text) / 32) + 1):
                split_text = text[(32 * i):(32 * (i + 1))]
                encrypt_text += RSA_Encrypt(self.key).encrypt(split_text)
            return encrypt_text

    @staticmethod
    def geneRandomToken():
        randomList = choices(ascii_letters + digits, k=129)
        token = f"V1.0{''.join(x for x in randomList)}"
        return token

    # 签到
    def chech_in(self):
        url = "https://wapside.189.cn:9001/jt-sign/api/home/sign"
        data = {
            "encode": AES_Ctypt("34d7cb0bcdf07523").encrypt(
                f'{{"phone":{self.phone},"date":{timestamp()},"signSource":"smlprgrm"}}')
        }
        print_now(self.req(url, "post", data))

    # 获取任务列表
    def get_task(self):
        url = "https://wapside.189.cn:9001/jt-sign/paradise/getTask"
        data = {
            "para": self.telecom_encrypt(f'{{"phone":{self.phone}}}')
        }
        msg = self.req(url, "post", data)
        # print_now(dumps(msg, indent=2, ensure_ascii=False))
        if msg["resoultCode"] == "0":
            self.task_list = msg["data"]
        else:
            print_now("获取任务列表失败")
            print_now(msg)
            return

    # 做每日任务
    def do_task(self):
        url = "https://wapside.189.cn:9001/jt-sign/paradise/polymerize"
        for task in self.task_list:
            if "翻牌抽好礼" in task["title"] or "查看我的订单" in task["title"] or "查看我的云盘" in task[
                "title"] or "查看权益中心" in task["title"] or "访问宽带余额" in task["title"] or "访问“我的宽带”" in \
                    task["title"] or "查看“装修进度”" in task["title"] or "查看视频彩铃" in task["title"]:
                # if "翻牌抽好礼" in task["title"] or "查看我的订单" in task["title"] or "查看我的云盘" in task["title"]:
                #print_now(f'{task["title"]}----{task["taskId"]}')
                #print_now(f'{task["title"]}')
                decrept_para = f'{{"phone":"{self.phone}","jobId":"{task["taskId"]}"}}'
                data = {
                    "para": self.telecom_encrypt(decrept_para)
                }
                data = self.req(url, "POST", data)
                if data["data"]["code"] == 0:
                    print(f'账号{self.phone} {task["title"]}-------------------{data["resoultMsg"]}')
                    # print_now(data)
                else:
                    print_now(f'账号{self.phone} 聚合任务完成失败,原因是{data["resoultMsg"]}')

    # 给宠物喂食
    def food(self):
        url = "https://wapside.189.cn:9001/jt-sign/paradise/food"
        data = {
            "para": self.telecom_encrypt(f'{{"phone":{self.phone}}}')
        }
        res_data = self.req(url, "POST", data)
        if res_data["resoultCode"] == "0":
            print_now(res_data["resoultMsg"])
        else:
            print_now(f'账号{self.phone} 聚合任务完成失败,原因是{res_data["resoultMsg"]}')

    # 查询宠物等级
    def get_level(self):
        url = "https://wapside.189.cn:9001/jt-sign/paradise/getParadiseInfo"
        body = {
            "para": self.telecom_encrypt(f'{{"phone":{self.phone}}}')
        }
        data = self.req(url, "POST", body)
        self.level = int(data["userInfo"]["paradiseDressup"]["level"])
        if self.level < 5:
            print_now(f"账号{self.phone} 当前等级小于5级 不领取等级权益")
            return
        url = "https://wapside.189.cn:9001/jt-sign/paradise/getLevelRightsList"
        right_list = self.req(url, "POST", body)[f"V{self.level}"]
        for data in right_list:
            # print(dumps(data, indent=2, ensure_ascii=0))
            if "00金豆" in data["righstName"] or "话费" in data["righstName"]:
                rightsId = data["id"]
                self.level_ex(rightsId)
                continue
        # print(self.rightsId)

    # 每月领取等级金豆
    def level_ex(self, rightsId):
        # self.get_level()
        url = "https://wapside.189.cn:9001/jt-sign/paradise/conversionRights"
        data = {
            "para": self.telecom_encrypt(f'{{"phone":{self.phone},"rightsId":"{rightsId}"}},"receiveCount":1')
        }
        print_now(self.req(url, "POST", data))

    # 查询连续签到天数
    def query_signinfo(self):
        url = "https://wapside.189.cn:9001/jt-sign/reward/activityMsg"
        body = {
            "para": self.telecom_encrypt(f'{{"phone":{self.phone}}}')
        }
        data = self.req(url, "post", body)
        # print(dumps(data, indent=2, ensure_ascii=0))
        recordNum = data["recordNum"]
        if recordNum != 0:
            return data["date"]["id"]
        return ""

    # 若连续签到为7天 则兑换
    def convert_reward(self):
        global msg_str #声明我们在函数内部使用的是在函数外部定义的全局变量msg_str
        url = "https://wapside.189.cn:9001/jt-sign/reward/convertReward"
        try:
            rewardId = self.query_signinfo()  # "baadc927c6ed4d8a95e28fa3fc68cb9"
        except:
            rewardId = "baadc927c6ed4d8a95e28fa3fc68cb9"
        if rewardId == "":
            return
        body = {
            "para": self.telecom_encrypt(
                f'{{"phone":"{self.phone}","rewardId":"{rewardId}","month":"{date.today().__format__("%Y%m")}"}}')
        }
        for i in range(10):
            try:
                data = self.req(url, "post", body)
            except Exception as e:
                print(f"请求发送失败: " + str(e))
                sleep(6)
                continue
            print_now(data)
            if data["code"] == "0":
                break
            sleep(6)
        reward_status = self.get_coin_info()
        if reward_status:
            self.msg += f"账号{self.phone}连续签到7天兑换2元话费成功\n"
            msg_str  += f"账号{self.phone}连续签到7天兑换2元话费成功\n"
            print_now(self.msg)
            #push("电信签到兑换", self.msg)
        else:
            self.msg += f"账号{self.phone}连续签到7天兑换2元话费失败 明天会继续尝试兑换\n"
            msg_str  += f"账号{self.phone}连续签到7天兑换2元话费失败 明天会继续尝试兑换\n"
            print_now(self.msg)
            #push("电信签到兑换", self.msg)

    # 查询金豆数量
    def coin_info(self):
        url = "https://wapside.189.cn:9001/jt-sign/api/home/userCoinInfo"
        data = {
            "para": self.telecom_encrypt(f'{{"phone":{self.phone}}}')
        }
        self.coin_count = self.req(url, "post", data)
        print_now(self.coin_count)

    def author(self):
        """
        通过usercode 获取 authorization
        :return:
        """
        self.get_usercode()
        url = "https://xbk.189.cn/xbkapi/api/auth/userinfo/codeToken"
        data = {
            "usercode": self.usercode
        }
        data = post(url, headers=self.headers_live, json=data).json()
        self.authorization = f"Bearer {data['data']['token']}"
        self.headers_live["Authorization"] = self.authorization

    def get_usercode(self):
        """
        授权星播客登录获取 usercode
        :return:
        """
        url = f"https://xbk.189.cn/xbkapi/api/auth/jump?userID={self.ticket}&version=9.3.3&type=room&l=renwu"
        self.headers_live = {
            "User-Agent": self.ua,
            "Host": "xbk.189.cn",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9"
        }
        location = get(url, headers=self.headers_live, allow_redirects=False).headers["location"]
        usercode = findall(r"usercode=(.*?)&", location)[0]
        self.usercode = usercode

    def watch_video(self):
        """
        看视频 一天可完成6次
        :return:
        """
        url = "https://xbk.189.cn/xbkapi/lteration/liveTask/index/watchVideo"
        data = {
            "articleId": 3453
        }
        data = post(url, headers=self.headers_live, json=data).json()
        if data["code"] == 0:
            print("账号{self.phone} 看小视频15s完成一次")
        else:
            print(f"账号{self.phone} 完成看小视频15s任务失败, 失败原因为{data['msg']}")

    def like(self):
        """
        点赞直播间 可完成5次
        :return:
        """
        url = "https://xbk.189.cn/xbkapi/lteration/room/like"
        liveId_list = [1820, 2032, 2466, 2565, 1094, 2422, 1858, 2346]
        shuffle(liveId_list)
        for liveId in liveId_list[:5]:
            data = {
                "account": self.phone,
                "liveId": liveId
            }
            try:
                data = post(url, headers=self.headers_live, json=data).json()
                if data["code"] == 8888:
                    sleep(2)
                    print(data["msg"])
                else:
                    print(f"账号{self.phone} 完成点赞直播间任务失败,原因是{data['msg']}")
            except Exception:
                print(Exception)

    def watch_live(self):
        # 首先初始化任务,等待15秒倒计时后再完成 可完成10次
        url = "https://xbk.189.cn/xbkapi/lteration/liveTask/index/watchLiveInit"
        live_id = randint(1000, 2700)
        data = {
            "period": 1,
            "liveId": live_id
        }
        data = post(url, headers=self.headers_live, json=data).json()
        if data["code"] == 0:
            taskcode = data["data"]
            url = "https://xbk.189.cn/xbkapi/lteration/liveTask/index/watchLive"
            data = {
                "key": taskcode,
                "period": 1,
                "liveId": live_id
            }
            print("正在等待15秒")
            sleep(15)
            data = post(url, headers=self.headers_live, json=data).json()
            if data["code"] == 0:
                print("账号{self.phone} 完成1次观看直播任务")
            else:
                print(f"账号{self.phone} 完成观看直播任务失败,原因是{data['msg']}")
        else:
            print(f"账号{self.phone} 初始化观看直播任务失败，失败原因为{data['msg']}")

    def get_userid(self):
        url = "https://wapside.189.cn:9001/jt-sign/api/home/homeInfo"
        body = {
            "para": self.telecom_encrypt(
                f'{{"phone":"{self.phone}","signDate":"{datetime.now().__format__("%Y-%m")}"}}')
        }
        userid = post(url, json=body).json()["data"]["userInfo"]["userThirdId"]
        return userid

    def share(self):
        """
        50的分享任务 token不做校检 有值即可 若登录成功了 使用自己的token 否则生成随机的token
        :return:
        """
        url = "https://appfuwu.189.cn:9021/query/sharingGetGold"
        body = {
            "headerInfos": {
                "code": "sharingGetGold",
                "timestamp": datetime.now().__format__("%Y%m%d%H%M%S"),
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": self.token if self.token != "" else self.geneRandomToken(),
                "userLoginName": self.phone
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "shareSource": "3",
                    "userId": self.get_userid(),
                    "account": TelecomLogin.get_phoneNum(self.phone)
                }
            }
        }
        headers = {
            "user-agent": "iPhone 14 Pro Max/9.6.1"
        }
        data = post(url, headers=headers, json=body).json()
        print_now(data)

    def main(self):
        global msg_str #声明我们在函数内部使用的是在函数外部定义的全局变量msg_str
        self.init()
        self.chech_in()
        self.get_task()
        self.do_task()
        if foods != 0:
            for i in range(foods):
                self.food()
        # self.convert_reward()
        if datetime.now().day == 1:
            self.get_level()
        self.share()
        # if self.ticket != "":
        #     self.author()
        #     for i in range(6):
        #         self.watch_video()
        #         sleep(15)
        #     self.like()
        #     for i in range(10):
        #         try:
        #             self.watch_live()
        #         except:
        #             continue
        self.coin_info()
        self.msg += f"\n账号{self.phone} 当前有金豆{self.coin_count['totalCoin']}\n"
        msg_str  += f"\n账号{self.phone} 当前有金豆{self.coin_count['totalCoin']}\n"
        #push("电信app签到", self.msg)
        
    def get_coin_info(self):
        url = "https://wapside.189.cn:9001/jt-sign/api/getCoinInfo"
        decrept_para = f'{{"phone":"{self.phone}","pageNo":0,"pageSize":10,type:"1"}}'
        data = {
            "para": self.telecom_encrypt(decrept_para)
        }
        data = self.req(url, "POST", data)
        
        try:
            if "skuName" in data["data"]["biz"]["results"][0] and "连续签到" in data["data"]["biz"]["results"][0]["skuName"]:
                return True
        except Exception as e:
                print(f"账号{self.phone}出现错误，请求失败结果: " )
                print_now(data)
        return False






def start(phone,password):
    if phone == "":
        exit(0)
    if password == "":
        print_now("电信服务密码未提供 只执行部分任务")
    if datetime.now().hour + (8 - int(strftime("%z")[2])) == 12:
        telecom = ChinaTelecom(phone, password, False)
        telecom.init()
        telecom.convert_reward()
    else:
        telecom = ChinaTelecom(phone, password)
        telecom.main()
    print("\n")




if __name__ == '__main__':
    l = []
    user_map = []
    cklist = get_cookie("TELECOM_PHONE_PASSWORD")
    for i in range(len(cklist)):
        #以#分割开的ck
        split1 = cklist[i].split("#")
        if len(split1)>1:
            for j in range(len(split1)):
                split2 = split1[j].split("&")
                if len(split2)>1:
                    user_map.append(split1[j])
        else:
            userinfo = cklist[i].split("&")
            if len(userinfo)>1:
                user_map.append(cklist[i])


                
    num_list = get_cookie("TELECOM_FOOD", 0, False)
    num = 0
    if num_list != 0:
        if len(num_list)>0:
            num = num_list[0]
    foods = int(float(num))
    for i in range(len(user_map)):
        phone=""
        password=""
        userinfo = user_map[i].split("&")
        if len(userinfo)>1:
            phone = userinfo[0]
            password = userinfo[1]
        print('开始执行第{}个账号：{}'.format((i+1),phone))
        if phone == "":
            print("当前账号未填写手机号 跳过")
            print("\n")
            continue
        p = threading.Thread(target=start,args=(phone,password))
        l.append(p)
        p.start()
        print("\n")
    for i in l:
        i.join()
    send("电信签到",msg_str)
