#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 19/5/2022 19:48
# -------------------------------
"""
1.无忧行app签到 请低调使用
2.cookie获取方式
    1.打开app-我的-任务中心 很多链接里(链接里 不是看headers)都有token 复制token的值填入环境变量即可 格式应该是 32位16进制数
    2.有效期不懂
3.cookie食用方式:只要token的值 32位16进制数 青龙运行可新建并放入到环境变量 WXY_TOKEN 中
"""
from json import loads, dumps
from base64 import b64decode, b64encode
from hashlib import md5 as md5Encode
from random import randint
from os import environ, system
from time import time

try:
    from Crypto.Cipher import AES
    from requests import post
except:
    print(
        "你还没有安装requests库和pycryptodome库 正在尝试自动安装 请在安装结束后重新执行此脚本\n若还是提示本条消息 请自行运行pip3 install requests和pip3 install pycryptodome或者在青龙的依赖管理里安装python的 requests 和 pycryptodome ")
    system("pip3 install pycryptodome")
    system("pip3 install requests")
    print("安装完成 脚本退出 请重新执行")
    exit(0)

token = environ.get("WXY_TOKEN") if environ.get("WXY_TOKEN") else ""
pushplus_token = environ.get("PUSH_PLUS_TOKEN") if environ.get("PUSH_PLUS_TOKEN") else ""
tgbot_token = environ.get("TG_BOT_TOKEN") if environ.get("TG_BOT_TOKEN") else ""
tg_userId = environ.get("TG_USER_ID") if environ.get("TG_USER_ID") else ""
tg_push_api = environ.get("TG_API_HOST") if environ.get("TG_API_HOST") else ""
if token == "":
    print("未填写token 请添加环境变量 WXY_TOKEN")
    exit(0)
if len(token) != 32:
    print("填写的token不对 是一个32位16进制数")
    exit(0)

BLOCK_SIZE = AES.block_size
# 不足BLOCK_SIZE的补位(s可能是含中文，而中文字符utf-8编码占3个位置,gbk是2，所以需要以len(s.encode())，而不是len(s)计算补码)
pad = lambda s: s + (BLOCK_SIZE - len(s.encode()) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s.encode()) % BLOCK_SIZE)
# 去除补位
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class AESCipher:
    def __init__(self, secretkey: str):
        self.key = secretkey  # 密钥
        # self.iv = secretkey[0:16]  # 偏移量

    def encrypt(self, text):
        """
        加密 ：先补位，再AES加密，后base64编码
        :param text: 需加密的明文
        :return:
        """
        # text = pad(text) 包pycrypto的写法，加密函数可以接受str也可以接受bytess
        text = pad(text).encode()  # 包pycryptodome 的加密函数不接受str
        cipher = AES.new(key=self.key.encode(), mode=AES.MODE_ECB)
        encrypted_text = cipher.encrypt(text)
        # 进行64位的编码,返回得到加密后的bytes，decode成字符串
        return b64encode(encrypted_text).decode('utf-8')

    def decrypt(self, encrypted_text):
        """
        解密 ：偏移量为key[0:16]；先base64解，再AES解密，后取消补位
        :param encrypted_text : 已经加密的密文
        :return:
        """
        encrypted_text = b64decode(encrypted_text)
        cipher = AES.new(key=self.key.encode(), mode=AES.MODE_ECB)
        decrypted_text = cipher.decrypt(encrypted_text)
        return unpad(decrypted_text).decode('utf-8')


class WYX:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Referer": "https://cdn.jegotrip.com.cn/"
        }
        self.ge = "93EFE107DDE6DE51"
        self.he = "online_jego_h5"
        self.fe = "01"
        self.taskId = ""
        self.msg = ""

    def timestamp(self):
        return int(time() * 1000)

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
            post(url, headers=headers, data=dumps(data))
        except:
            print('推送失败')

    def tgpush(self, content):
        url = f"https://api.telegram.org/bot{tgbot_token}/sendMessage"
        if tg_push_api != "":
            url = f"https://{tg_push_api}/bot{tgbot_token}/sendMessage"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'chat_id': str(tg_userId), 'text': content, 'disable_web_page_preview': 'true'}
        try:
            post(url, headers=headers, data=data, timeout=10)
        except:
            print('推送失败')

    def push(self, msg):
        if pushplus_token != "":
            self.pushplus("无忧行签到", msg)
        if tgbot_token != "" and tg_userId != "":
            self.tgpush(f"无忧行签到\n{msg}")

    def md5(self, text):
        m = md5Encode(text.encode(encoding='utf-8'))
        return m.hexdigest()

    def decrypt_key(self, encrypt_key):
        t = b64decode(encrypt_key).decode()
        a = t.split(";")
        if a and 3 == len(a):
            c = self.ge + a[1]
            n = self.md5(c)[8:24]
            return n

    def gene_encrypt_key(self):
        e = f"{self.timestamp()}{randint(100, 999)}"
        i = self.ge + e
        a = self.md5(i)[8:24]
        c = f"{self.he};{e};{self.fe}"
        t = b64encode(c.encode("utf-8")).decode()
        return a, t

    """查询总积分"""

    def query_total_score(self):
        url = f"https://app.jegotrip.com.cn/api/service/member/v1/expireRewardQuery?token={self.token}&h_token={self.token}&lang=zh_CN"
        encrypt_key = self.gene_encrypt_key()
        key = encrypt_key[0]
        sec = encrypt_key[1]
        body = {
            "sec": sec,
            "body": AESCipher(key).encrypt("{}")
        }
        encrypt_data = post(url, headers=self.headers, json=body).json()
        if encrypt_data["code"] == "0":
            encrypt_body = encrypt_data["body"]
            encrypt_sec = encrypt_data["sec"]
            decrypt_data = AESCipher(self.decrypt_key(encrypt_sec)).decrypt(encrypt_body)
            total_score = loads(decrypt_data)["tripcoins"]
            print(f"查询成功, 你共有{total_score}点积分")
            self.msg += f", 你共有{total_score}点积分"

    def get_checkin_taskid(self):
        url = f"https://app.jegotrip.com.cn/api/service/v1/mission/sign/querySign?token={self.token}&h_token={self.token}&lang=zh_CN"
        encrypt_key = self.gene_encrypt_key()
        key = encrypt_key[0]
        sec = encrypt_key[1]
        body = {
            "sec": sec,
            "body": AESCipher(key).encrypt("{}")
        }
        encrypt_data = post(url, headers=self.headers, json=body).json()
        if encrypt_data["code"] == "0":
            encrypt_body = encrypt_data["body"]
            encrypt_sec = encrypt_data["sec"]
            decrypt_data = AESCipher(self.decrypt_key(encrypt_sec)).decrypt(encrypt_body)
            for checkin_task in eval(decrypt_data)[::-1]:
                task_status = checkin_task["isSign"]
                if task_status == 2:
                    self.taskId = checkin_task["id"]
                    # print(self.taskId)
                    return self.taskId

        if self.taskId == "":
            print("获取任务id失败 退出")
            exit(0)

    def checkin(self):
        url = f"https://app.jegotrip.com.cn/api/service/v1/mission/sign/userSign?token={self.token}&h_token={self.token}&lang=zh_CN"
        encrypt_key = self.gene_encrypt_key()
        key = encrypt_key[0]
        sec = encrypt_key[1]
        body = {
            "sec": sec,
            "body": AESCipher(key).encrypt(f'{{"signConfigId":{self.get_checkin_taskid()}}}')
        }
        data = post(url, headers=self.headers, json=body).json()
        if data["code"] == "0":
            self.msg += "签到成功"
            print(self.msg)
        else:
            self.msg += "签到失败"
            print(self.msg)

    def main(self):
        self.checkin()
        self.query_total_score()
        self.push(self.msg)


if __name__ == "__main__":
    WYX(token).main()
