#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/9/16 17:20
# -------------------------------
from json import dumps
from requests import post
from uuid import uuid1

from tool import print_now, md5, timestamp

class SFLogin:
    def __init__(self):
        self.deviceId = str(uuid1())
    def getSytToken(self, body, deviceId, timestamp):
        wait_encrypt_str = f"CNsc{md5(body)}9.37.2{deviceId}172b34b80bac04ad148a2729dfb2cd9f{timestamp}"
        sytToken = md5(wait_encrypt_str)
        return sytToken
    def sendMsgCaptcha(self):
        url = "https://ccsp-egmas.sf-express.com/cx-app-member/member/app/user/sendCaptcha"
        self.phone = input("请输入手机号(输入完成后按回车结束): ")
        if len(self.phone) != 11:
            print_now("手机号格式错误")
        timestamp1 = timestamp()
        body = f'{{"mobile":{self.phone},"type":"05"}}'
        headers = {
            "regioncode": "CN",
            "languagecode": "sc",
            "screensize": "1080x1920",
            "mediacode": "AndroidML",
            "systemversion": "12",
            "clientversion": "9.37.2",
            "model": "SM-G9860",
            "carrier": "unknown",
            "deviceid": self.deviceId,
            "jsbundle": "172b34b80bac04ad148a2729dfb2cd9f",
            "timeinterval": str(timestamp1),
            "syttoken": self.getSytToken(body, self.deviceId, timestamp1),
            "content-type": "application/json; charset=utf-8",
            "content-length": str(len(dumps(body).replace(" ", ""))),
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.1",
            "pragma": "no-cache",
            "cache-control": "no-cache"
        }
        data = post(url, headers=headers, data=body).json()
        if not data.get("success"):
            print(f"发送验证码失败, 请重试, 发送日志为{data}")
    def login(self):
        url = "https://ccsp-egmas.sf-express.com/cx-app-member/member/app/user/userLogin"
        timestamp1 = timestamp()
        captcha = input("请输入手机短信验证码(有效期90秒, 输入完成后按回车结束): ")
        body = f'{{"captcha":"{captcha}","mobile":"{self.phone}","registerSource":""}}'
        headers = {
            "regioncode": "CN",
            "languagecode": "sc",
            "screensize": "1080x1920",
            "mediacode": "AndroidML",
            "systemversion": "12",
            "clientversion": "9.37.2",
            "model": "SM-G9860",
            "carrier": "unknown",
            "deviceid": self.deviceId,
            "jsbundle": "172b34b80bac04ad148a2729dfb2cd9f",
            "timeinterval": str(timestamp1),
            "syttoken": self.getSytToken(body, self.deviceId, timestamp1),
            "content-type": "application/json; charset=utf-8",
            "content-length": str(len(dumps(body).replace(" ", ""))),
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.1",
            "pragma": "no-cache",
            "cache-control": "no-cache"
        }
        login_data = post(url, headers=headers, data=body).json()
        if not login_data.get("success"):
            print_now(f"登陆失败, 登录接口日志为{login_data}")
            exit(0)
        self.menNo = login_data["obj"]["memNo"]
        self.userId = login_data["obj"]["memberId"]
    def get_sign(self):
        url = "https://ccsp-egmas.sf-express.com/cx-app-member/member/app/user/universalSign"
        body = f'{{"needReqTime":"1","memNo":"{self.menNo}","mobile":"{self.phone}","userId":"{self.userId}","extra":"","name":"mcs-mimp-web.sf-express.com"}}'
        timestamp1 = timestamp()
        headers = {
            "Host": "ccsp-egmas.sf-express.com",
            "User-Agent": "okhttp/4.9.1",
            "languageCode": "sc",
            "clientVersion": "9.37.2",
            "mediaCode": "AndroidML",
            "systemVersion": "12",
            "regionCode": "CN",
            "jsbundle": "172b34b80bac04ad148a2729dfb2cd9f",
            "Content-Length": str(len(dumps(body).replace(" ", ""))),
            "deviceId": self.deviceId, # 0ea5f454-0086-345f-b14f-d06b65d868b9
            "Connection": "keep-alive",
            "sytToken": self.getSytToken(body, self.deviceId, timestamp1),
            "carrier": "unknown",
            "Accept-Language": "zh-Hans-JP;q=1, zh-Hant-JP;q=0.9, en-JP;q=0.8",
            "model": "SM-G9860",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "timeInterval": str(timestamp1),
            "screenSize": "1080x1920"
        }
        req = post(url, headers=headers, data=body)
        sign = req.json()["obj"]["sign"]
        # sign = str(sign).replace("+", "%2B")
        # sign = str(sign).replace("/", "%2F")
        print_now("以下是你的sign, 请复制后自行使用, 部分环境下需要如111和112行一样 将 + 转化成%2B / 转化成%2F")
        print_now(sign)
        return
    def main(self):
        self.sendMsgCaptcha()
        self.login()
        self.get_sign()
if __name__ == "__main__":
    SFLogin().main()
