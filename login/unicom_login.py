#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2023/2/2 19:00
# cron "" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('某通app短信登录');
# -------------------------------
"""
某通短信登录获取online_token 抄自 小一佬 github@https://github.com/xream 感谢
1. 建议获取本机appid 新建环境变量 CHINA_UNICOM_APPID 填入本机appid再使用 获取方法搜索引擎自行搜索
2. 因青龙面板无法进行控制台交互 故设置了两种运行方式
    i.面板内新建任务 直接运行按提示增加环境变量即可
    ii.docker容器内运行 进入login文件夹内 输入命令 (python3 unicom_login.py 114514)(不要带着括号) 按提示输入对应的东西回车即可
3. 若未填本机appid 脚本会生成随机的 但经热心群友测试反馈 不一定能用 也有能用的 若不能用 尝试将脚本输出的appid换成本机的appid 有群友这样操作可以正常使用
4. 此登录脚本只提供另一种方案 建议还是自己抓包 不会有顶号导致无效的问题
"""
from requests import post
from urllib.parse import quote
from time import sleep
from uuid import uuid4
from sys import path, argv
path.append("../tools")
from tool import print_now, get_environ
from rsa_encrypt import RSA_Encrypt
class UnicomLogin:
    rsa_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDc+CZK9bBA9IU+gZUOc6FUGu7y\nO9WpTNB0PzmgFBh96Mg1WrovD1oqZ+eIF4LjvxKXGOdI79JRdve9NPhQo07+uqGQ\ngE4imwNnRx7PFtCRryiIEcUoavuNtuRVoBAm6qdB0SrctgaqGfLgKvZHOnwTjyNq\njBUxzMeQlEC2czEMSwIDAQAB\n-----END PUBLIC KEY-----"
    def __init__(self, account, run_mode):
        self.account = account
        interim_appid = get_environ("CHINA_UNICOM_APPID", output=False)
        self.appid = "".join([uuid4().hex for i in range(5)]) if len(interim_appid) != 160 else interim_appid
        self.run_mode = run_mode
    def send_sms_code(self):
        url = "https://m.client.10010.com/mobileService/sendRadomNum.htm"
        body = f"mobile={quote(RSA_Encrypt(UnicomLogin.rsa_key).encrypt(self.account, b64=True))}&version=android@10.0100"
        headers = {
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 13; SM-S908U Build/TP1A.220624.014);unicom{version:android@10.0100}",
            "content-type": "application/x-www-form-urlencoded"
        }
        data = post(url, headers=headers, data=body).json()
        if data["rsp_code"] == "0000":
            print("发送短信验证码成功")
            if self.run_mode == "hand":
                self.login(input("请输入短信验证码(输入完成后按回车键结束): "))
                return
            print_now("请5分钟内新建环境变量 UNICOM_SMS 值为收到的四位数短信验证码 然后再次运行")


    def login(self, captcha):
        url = "https://m.client.10010.com/mobileService/radomLogin.htm"
        body = f"mobile={quote(RSA_Encrypt(UnicomLogin.rsa_key).encrypt(self.account, b64=True))}&version=android%4010.0100&password={quote(RSA_Encrypt(UnicomLogin.rsa_key).encrypt(captcha, b64=True))}&appId={self.appid}"
        headers = {
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 13; SM-S908U Build/TP1A.220624.014);unicom{version:android@10.0100}",
            "content-type": "application/x-www-form-urlencoded"
        }
        data = post(url, headers=headers, data=body).json()
        print(data)
        if "token_online" in data:
            print("登录获取数据成功")
            print(f"请设置环境变量 UNICOM_GAME_ACCOUNT_INFO 为 {self.account}#{self.appid}#{data['token_online']}")
    def main(self):
        print_now("如果不是刚刚获取已经运行获取验证码 请先将 UNICOM_SMS 删除或者清空")
        if len(argv) == 1:
            captcha = get_environ("UNICOM_SMS", output=False)
            if len(captcha) < 4:
                self.send_sms_code()
            else:
                self.login(captcha)
        else:
            self.send_sms_code()
if __name__ == '__main__':
    run_mode = "ql" if len(argv) == 1 else "hand"
    if run_mode == "ql":
        account = get_environ("LOGIN_UNICOM_PHONE")
    else:
        account = input("请输入手机号(按回车键结束输入): ")
    if account == "":
        exit(0)
    UnicomLogin(account, run_mode).main()