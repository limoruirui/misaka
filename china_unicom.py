#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/8/10 13:23
# -------------------------------
# cron "30 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('某通阅读');
"""
联通app抽奖 入口:联通app 搜索 阅读专区 进入话费派送中
1. 脚本仅供学习交流使用, 请在下载后24h内删除
2. 需要第三方库 pycryptodome 支持 命令行安装 pip3 install pycryptodome或者根据自己环境自行安装
3. 环境变量说明 PHONE_NUM(必需) UNICOM_LOTTER(选填) 自行新建环境变量添加
    PHONE_NUM 为你的手机号
    UNICOM_LOTTER 默认自动抽奖, 若不需要 则添加环境变量值为 False
    推送通知的变量同青龙 只写了tgbot(支持反代api)和pushplus
"""
"""
updateTime: 2022.12.1  log: 活动重新上架 改用 pycryptodome 替代 cryptography 进行aes加密
updateTime: 2022.9.1  log: 每个月活动id改变更新
"""

from requests import post
from time import sleep, time
from datetime import datetime
from hashlib import md5 as md5Encode
from random import randint, uniform
from os import environ
from sys import stdout, exit
from base64 import b64encode
from json import dumps

from tools.encrypt_symmetric import Crypt
from tools.send_msg import push
from tools.tool import get_environ, random_sleep
random_sleep(0, 1600)


"""主类"""
class China_Unicom:
    def __init__(self, phone_num):
        self.phone_num = phone_num
        self.headers = {
            "Host": "10010.woread.com.cn",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://10010.woread.com.cn",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{randint(89, 103)}.0.{randint(100, 999)}.{randint(100, 999)} Safari/537.36",
            "Connection": "keep-alive",
            "Referer": "https://10010.woread.com.cn/ng_woread/",
        }
        self.fail_num = 0

    def timestamp(self):
        return round(time() * 1000)

    def print_now(self, content):
        print(content)
        stdout.flush()

    def md5(self, str):
        m = md5Encode(str.encode(encoding='utf-8'))
        return m.hexdigest()

    def req(self, url, crypt_text):
        body = {
            "sign": b64encode(Crypt(crypt_type="AES", key=self.headers["accesstoken"][-16:], iv="16-Bytes--String", mode="CBC").encrypt(crypt_text).encode()).decode()
        }
        self.headers["Content-Length"] = str(len(dumps(body).replace(" ", "")))
        data = post(url, headers=self.headers, json=body).json()
        return data

    def referer_login(self):
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        timestamp = self.timestamp()
        url = f"https://10010.woread.com.cn/ng_woread_service/rest/app/auth/10000002/{timestamp}/{self.md5(f'100000027k1HcDL8RKvc{timestamp}')}"
        crypt_text = f'{{"timestamp":"{date}"}}'
        body = {
            "sign": b64encode(Crypt(crypt_type="AES", key="1234567890abcdef").encrypt(crypt_text).encode()).decode()
        }
        self.headers["Content-Length"] = str(len(str(body)) - 1)
        data = post(url, headers=self.headers, json=body).json()
        if data["code"] == "0000":
            self.headers["accesstoken"] = data["data"]["accesstoken"]
        else:
            self.print_now(f"设备登录失败,日志为{data}")
            exit(0)

    def get_userinfo(self):
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        url = "https://10010.woread.com.cn/ng_woread_service/rest/account/login"
        crypt_text = f'{{"phone":"{self.phone_num}","timestamp":"{date}"}}'
        data = self.req(url, crypt_text)
        if data["code"] == "0000":
            self.userinfo = data["data"]
        else:
            self.print_now(f"手机号登录失败, 日志为{data}")
            exit(0)

    def watch_video(self):
        self.print_now("看广告获取积分任务: ")
        url = "https://10010.woread.com.cn/ng_woread_service/rest/activity/yearEnd/obtainScoreByAd"
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        crypt_text = f'{{"value":"947728124","timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
        for i in range(3):
            data = self.req(url, crypt_text)
            self.print_now(data)
            if self.fail_num == 3:
                self.print_now("当前任务出现异常 且错误次数达到3次 请手动检查")
                push("某通阅读", "当前任务出现异常 且错误次数达到3次 请手动检查")
                exit(0)
            if data["code"] == "9999":
                self.print_now("当前任务出现异常 正在重新执行")
                self.fail_num += 1
                self.main()
            sleep(uniform(2, 8))

    def read_novel(self):
        self.print_now("正在执行观看150次小说, 此过程较久, 最大时长为150 * 8s = 20min")
        for i in range(150):
            date = datetime.today().__format__("%Y%m%d%H%M%S")
            chapterAllIndex = randint(100000000, 999999999)
            cntIndex = randint(1000000, 9999999)
            url = f"https://10010.woread.com.cn/ng_woread_service/rest/cnt/wordsDetail?catid={randint(100000, 999999)}&pageIndex={randint(10000, 99999)}&cardid={randint(10000, 99999)}&cntindex={cntIndex}&chapterallindex={chapterAllIndex}&chapterseno=3"
            crypt_text = f'{{"chapterAllIndex":{chapterAllIndex},"cntIndex":{cntIndex},"cntTypeFlag":"1","timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
            self.req(url, crypt_text)
            sleep(uniform(2, 8))

    def query_score(self):
        url = "https://10010.woread.com.cn/ng_woread_service/rest/activity/yearEnd/queryUserScore"
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        crypt_text = f'{{"activeIndex":{self.activeIndex},"timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
        data = self.req(url, crypt_text)
        total_score = data["data"]["validScore"]
        self.lotter_num = int(total_score / 50)
        self.print_now(f"你的账号当前有积分{total_score}, 可以抽奖{self.lotter_num}次")

    def get_activetion_id(self):
        url = "https://10010.woread.com.cn/ng_woread_service/rest/activity/yearEnd/queryActiveInfo"
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        crypt_text = f'{{"timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
        data = self.req(url, crypt_text)
        if data["code"] == "0000":
            self.activeIndex = data["data"]["activeindex"]
        else:
            self.print_now(f"活动id获取失败 将影响抽奖和查询积分")

    def lotter(self):
        url = "https://10010.woread.com.cn/ng_woread_service/rest/activity/yearEnd/handleDrawLottery"
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        crypt_text = f'{{"activeIndex":{self.activeIndex},"timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
        data = self.req(url, crypt_text)
        if data["code"] == "0000":
            self.print_now(f"抽奖成功, 获得{data['data']['prizename']}")
        else:
            self.print_now(f"抽奖失败, 日志为{data}")

    def watch_ad(self):
        self.print_now("观看广告得话费红包: ")
        url = "https://10010.woread.com.cn/ng_woread_service/rest/activity/userTakeActive"
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        crypt_text = f'{{"activeIndex":6880,"timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
        data = self.req(url, crypt_text)
        self.print_now(data)

    def exchange(self):
        # ticketValue activeid来自于https://10010.woread.com.cn/ng_woread_service/rest/phone/vouchers/getSysConfig get请求
        # {"ticketValue":"300","activeid":"61yd210901","timestamp":"20220816213709","token":"","userId":"","userIndex":,"userAccount":"","verifyCode":""}
        url = "https://10010.woread.com.cn/ng_woread_service/rest/phone/vouchers/exchange"
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        crypt_text = f'{{"ticketValue":"300","activeid":"61yd210901","timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
        data = self.req(url, crypt_text)
        print(data)

    def query_red(self):
        url = "https://10010.woread.com.cn/ng_woread_service/rest/phone/vouchers/queryTicketAccount"
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        crypt_text = f'{{"timestamp":"{date}","token":"{self.userinfo["token"]}","userId":"{self.userinfo["userid"]}","userIndex":{self.userinfo["userindex"]},"userAccount":"{self.userinfo["phone"]}","verifyCode":"{self.userinfo["verifycode"]}"}}'
        data = self.req(url, crypt_text)
        if data["code"] == "0000":
            can_use_red = data["data"]["usableNum"] / 100
            if can_use_red >= 3:
                self.print_now(f"查询成功 你当前有话费红包{can_use_red} 可以去兑换了")
                push("某通阅读", f"查询成功 你当前有话费红包{can_use_red} 可以去兑换了")
            else:
                self.print_now(f"查询成功 你当前有话费红包{can_use_red} 不足兑换的最低额度")
                push("某通阅读", f"查询成功 你当前有话费红包{can_use_red} 不足兑换的最低额度")

    def main(self):
        self.referer_login()
        self.get_userinfo()
        self.watch_video()
        self.get_activetion_id()
        self.read_novel()
        self.query_score()
        self.watch_ad()
        if unicom_lotter:
            for i in range(self.lotter_num):
                self.lotter()
                sleep(2)
            self.query_score()
        self.query_red()
        exit(0)


if __name__ == "__main__":
    """读取环境变量"""
    phone_num = get_environ("PHONE_NUM")
    unicom_lotter = environ.get("UNICOM_LOTTER") if environ.get("UNICOM_LOTTER") else True
    if phone_num == "":
        exit(0)
    China_Unicom(phone_num).main()
