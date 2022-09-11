#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/8/10 13:23
# -------------------------------
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
updateTime: 2022.9.1  log: 每个月活动id改变更新
"""
import base64

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class PrpCrypt(object):

    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'16-Bytes--String')
        text = text.encode('utf-8')

        # 这里**key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用

        text = self.pkcs7_padding(text)

        self.ciphertext = cryptor.encrypt(text)

        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        padded_data = padder.update(data) + padder.finalize()

        return padded_data

    @staticmethod
    def pkcs7_unpadding(padded_data):
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data)

        try:
            uppadded_data = data + unpadder.finalize()
        except ValueError:
            raise Exception('无效的加密信息!')
        else:
            return uppadded_data

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        # 偏移量'abcdefg'
        cryptor = AES.new(self.key, self.mode, b'16-Bytes--String')
        plain_text = cryptor.decrypt(a2b_hex(text))
        # return plain_text.rstrip('\0')
        return bytes.decode(plain_text).rstrip('\0')


from requests import post
from time import sleep, time
from datetime import datetime
from hashlib import md5 as md5Encode
from random import randint, uniform
from os import environ
from sys import stdout, exit

"""读取环境变量"""
phone_num = environ.get("PHONE_NUM") if environ.get("PHONE_NUM") else ""
unicom_lotter = environ.get("UNICOM_LOTTER") if environ.get("UNICOM_LOTTER") else True
pushplus_token = environ.get("PUSH_PLUS_TOKEN") if environ.get("PUSH_PLUS_TOKEN") else ""
tgbot_token = environ.get("TG_BOT_TOKEN") if environ.get("TG_BOT_TOKEN") else ""
tg_userId = environ.get("TG_USER_ID") if environ.get("TG_USER_ID") else ""
tg_push_api = environ.get("TG_API_HOST") if environ.get("TG_API_HOST") else ""
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

    def pushplus(self, title, content):
        url = "http://www.pushplus.plus/send"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "token": pushplus_token,
            "title": title,
            "content": content
        }
        try:
            post(url, headers=headers, json=data)
        except:
            self.print_now('推送失败')

    def tgpush(self, content):
        url = f"https://api.telegram.org/bot{tgbot_token}/sendMessage"
        if tg_push_api != "":
            url = f"https://{tg_push_api}/bot{tgbot_token}/sendMessage"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'chat_id': str(tg_userId), 'text': content, 'disable_web_page_preview': 'true'}
        try:
            post(url, headers=headers, data=data, timeout=10)
        except:
            self.print_now('推送失败')

    def push(self, msg):
        if pushplus_token != "":
            self.pushplus("联通app大转盘", msg)
        if tgbot_token != "" and tg_userId != "":
            self.tgpush(f"联通app大转盘:\n{msg}")

    def req(self, url, crypt_text):
        body = {
            "sign": base64.b64encode(PrpCrypt(self.headers["accesstoken"][-16:]).encrypt(crypt_text)).decode()
        }
        self.headers["Content-Length"] = str(len(str(body)) - 1)
        data = post(url, headers=self.headers, json=body).json()
        return data

    def referer_login(self):
        date = datetime.today().__format__("%Y%m%d%H%M%S")
        timestamp = self.timestamp()
        url = f"https://10010.woread.com.cn/ng_woread_service/rest/app/auth/10000002/{timestamp}/{self.md5(f'100000027k1HcDL8RKvc{timestamp}')}"
        crypt_text = f'{{"timestamp":"{date}"}}'
        body = {
            "sign": base64.b64encode(PrpCrypt("1234567890abcdef").encrypt(crypt_text)).decode()
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
                self.push("当前任务出现异常 且错误次数达到3次 请手动检查")
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
        body = {
            "sign": base64.b64encode(PrpCrypt(self.headers["accesstoken"][-16:]).encrypt(crypt_text)).decode()
        }
        self.headers["Content-Length"] = str(len(str(body)) - 1)
        data = self.req(url, crypt_text)
        if data["code"] == "0000":
            can_use_red = data["data"]["usableNum"] / 100
            if can_use_red >= 3:
                self.print_now(f"查询成功 你当前有话费红包{can_use_red} 可以去兑换了")
                self.push(f"查询成功 你当前有话费红包{can_use_red} 可以去兑换了")
            else:
                self.print_now(f"查询成功 你当前有话费红包{can_use_red} 不足兑换的最低额度")
                self.push(f"查询成功 你当前有话费红包{can_use_red} 不足兑换的最低额度")

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
    China_Unicom(phone_num).main()
