#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/10/24 17:52
# -------------------------------
"""
营业厅登录获取token loginAuthCipherAsymmertric参数解密参考自 github@QGCliveDavis https://github.com/QGCliveDavis 感谢大佬
"""
from requests import post
from datetime import datetime
from xml.etree.ElementTree import XML
from uuid import uuid4
from sys import path
if "telecom_login" in __file__:
    path.append("../tools")
    from rsa_encrypt import RSA_Encrypt
    from encrypt_symmetric import Crypt
    from tool import print_now
else:
    from tools.rsa_encrypt import RSA_Encrypt
    from tools.tool import print_now
class TelecomLogin:
    def __init__(self, account, pwd):
        self.account = account
        self.pwd = pwd
        self.deviceUid = uuid4().hex
    def login(self):
        url = "https://appgologin.189.cn:9031/login/client/userLoginNormal"
        timestamp = datetime.now().__format__("%Y%m%d%H%M%S")
        key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofd\nWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18\nqFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMi\nPMpq0/XKBO8lYhN/gwIDAQAB\n-----END PUBLIC KEY-----"
        body = {
            "headerInfos": {
                "code": "userLoginNormal",
                "timestamp": timestamp,
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": "",
                "userLoginName": self.account
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "loginType": "4",
                    "accountType": "",
                    "loginAuthCipherAsymmertric": RSA_Encrypt(key).encrypt(f"iPhone 14 15.4.{self.deviceUid[:12]}{self.account}{timestamp}{self.pwd}0$$$0.", b64=True),
                    "deviceUid": self.deviceUid[:16],
                    "phoneNum": self.get_phoneNum(self.account),
                    "isChinatelecom": "0",
                    "systemVersion": "15.4.0",
                    "authentication": self.pwd
                }
            }
        }
        headers = {
            "user-agent": "iPhone 14 Pro Max/9.6.1",

        }

        data = post(url, headers=headers, json=body).json()
        code = data["responseData"]["resultCode"]
        if code != "0000":
            print_now("登陆失败, 接口日志" + str(data))
            return None
        self.token = data["responseData"]["data"]["loginSuccessResult"]["token"]
        self.userId = data["responseData"]["data"]["loginSuccessResult"]["userId"]
        return True

    def get_ticket(self):
        url = "https://appgologin.189.cn:9031/map/clientXML"
        body = f"<Request>\n<HeaderInfos>\n		<Code>getSingle</Code>\n		<Timestamp>{datetime.now().__format__('%Y%m%d%H%M%S')}</Timestamp>\n		<BroadAccount></BroadAccount>\n		<BroadToken></BroadToken>\n		<ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType>\n		<ShopId>20002</ShopId>\n		<Source>110003</Source>\n		<SourcePassword>Sid98s</SourcePassword>\n		<Token>{self.token}</Token>\n		<UserLoginName>{self.account}</UserLoginName>\n	</HeaderInfos>\n	<Content>\n		<Attach>test</Attach>\n		<FieldData>\n			<TargetId>{self.encrypt_userid(self.userId)}</TargetId>\n			<Url>4a6862274835b451</Url>\n		</FieldData>\n	</Content>\n</Request>"
        headers = {
            "User-Agent": "samsung SM-G9750/9.4.0",
            "Content-Type": "text/xml; charset=utf-8",
            "Content-Length": "694",
            "Host": "appgologin.189.cn:9031",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        xml_data = post(url, headers=headers, data=body).text
        doc = XML(xml_data)
        secret_ticket = doc.find("ResponseData/Data/Ticket").text
        # print("secret: " + secret_ticket)
        ticket = self.decrypt_ticket(secret_ticket)
        # print("ticket: " + ticket)
        return ticket, self.token
    def main(self):
        if self.login() is None:
            return "", ""
        userLoginInfo = self.get_ticket()
        return userLoginInfo
    @staticmethod
    def get_phoneNum(phone):
        result = ""
        for i in phone:
            result += chr(ord(i) + 2)
        return result
    @staticmethod
    def decrypt_ticket(secret_ticket):
        key = "1234567`90koiuyhgtfrdewsaqaqsqde"
        iv = "\0\0\0\0\0\0\0\0"
        # ticket = des3_cbc_decrypt(key, bytes(TelecomLogin.process_text(secret_ticket)), iv)
        ticket = Crypt("des3", key, iv, "CBC").decrypt(TelecomLogin.process_text(secret_ticket))
        return ticket
    @staticmethod
    def encrypt_userid(userid):
        key = "1234567`90koiuyhgtfrdewsaqaqsqde"
        iv = bytes([0] * 8)
        targetId = Crypt("des3", key, iv, "CBC").encrypt(userid)
        return targetId

    @staticmethod
    def process_text(text):
        length = len(text) >> 1
        bArr = [0] * length
        if len(text) % 2 == 0:
            i2 = 0
            i3 = 0
            while i2 < length:
                i4 = i3 + 1
                indexOf = "0123456789abcdef0123456789ABCDEF".find(text[i3])
                if indexOf != -1:
                    bArr[i2] = (((indexOf & 15) << 4) + ("0123456789abcdef0123456789ABCDEF".find(text[i4]) & 15))
                    i2 += 1
                    i3 = i4 + 1
                else:
                    print("转化失败 大概率是明文输入错误")
        return bArr
