#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 17/5/2022 19:26
# -------------------------------

"""
1.爱奇艺每月领取会员天数红包脚本 请低调使用 请不要用于商业牟利
2.每个号每个月能领三个 会员等级大于等于5级可以发给别人领 请自行斟酌设置crontab
3.cookie获取方式
    1.cookie可以用别人loon、qx等软件的mitm类自动获取再去boxjs里复制出来填写到环境变量或本脚本中
    2.也可以自行抓包 电脑或者手机都可以, 已知电脑不顶号的情况下有效期为三个月
4.cookie食用方式: 可以只保留P00001=xxx;中xxx的值 也可以整段都要 青龙运行可新建并放入到环境变量 iqy_ck 中 也可以直接填写在本脚本中
"""
cookie = ""
from time import sleep, time
from random import choice
from json import dumps
from hashlib import md5 as md5Encode
from string import digits, ascii_lowercase, ascii_uppercase
from sys import exit, stdout
from os import environ, system
from re import findall

try:
    from requests import Session, get, post
    from fake_useragent import UserAgent
except:
    print(
        "你还没有安装requests库和fake_useragent库 正在尝试自动安装 请在安装结束后重新执行此脚本\n若还是提示本条消息 请自行运行pip3 install requests和pip3 install fake-useragent或者在青龙的依赖管理里安装python的requests和fake-useragent")
    system("pip3 install fake-useragent")
    system("pip3 install requests")
    print("安装完成 脚本退出 请重新执行")
    exit(0)
iqy_ck = environ.get("iqy_ck") if environ.get("iqy_ck") else cookie
pushplus_token = environ.get("PUSH_PLUS_TOKEN") if environ.get("PUSH_PLUS_TOKEN") else ""
tgbot_token = environ.get("TG_BOT_TOKEN") if environ.get("TG_BOT_TOKEN") else ""
tg_userId = environ.get("TG_USER_ID") if environ.get("TG_USER_ID") else ""
tg_push_api = environ.get("TG_API_HOST") if environ.get("TG_API_HOST") else ""
if iqy_ck == "":
    print("未填写cookie 青龙可在环境变量设置 iqy_ck 或者在本脚本文件上方将获取到的cookie填入cookie中")
    exit(0)
if "P00001" in iqy_ck:
    iqy_ck = findall(r"P00001=(.*?)(;|$)", iqy_ck)[0][0]


class Iqiyi:
    def __init__(self, ck):
        self.ck = ck
        self.session = Session()
        self.user_agent = UserAgent().chrome
        self.headers = {
            "User-Agent": self.user_agent,
            "Cookie": f"P00001={self.ck}",
            "Content-Type": "application/json"
        }
        self.msg = ""
        self.redNo = ""
        self.last_num = 0

    """工具"""

    def req(self, url, req_method="GET", body=None):
        data = {}
        if req_method.upper() == "GET":
            try:
                data = self.session.get(url, headers=self.headers, params=body).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            #     data = self.session.get(url, headers=self.headers, params=body).text
            return data
        elif req_method.upper() == "POST":
            try:
                data = self.session.post(url, headers=self.headers, data=dumps(body)).json()
            except:
                self.print_now("请求发送失败,可能为网络异常")
            #     data = self.session.post(url, headers=self.headers, data=dumps(body)).text
            return data
        elif req_method.upper() == "OTHER":
            try:
                self.session.get(url, headers=self.headers, params=dumps(body))
            except:
                self.print_now("请求发送失败,可能为网络异常")
        else:
            self.print_now("您当前使用的请求方式有误,请检查")

    def timestamp(self, short=False):
        if (short):
            return int(time())
        return int(time() * 1000)

    def md5(self, str):
        m = md5Encode(str.encode(encoding='utf-8'))
        return m.hexdigest()

    def uuid(self, num, upper=False):
        str = ''
        if upper:
            for i in range(num):
                str += choice(digits + ascii_lowercase + ascii_uppercase)
        else:
            for i in range(num):
                str += choice(digits + ascii_lowercase)
        return str

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
            self.pushplus("爱奇艺每月领取会员", msg)
        if tgbot_token != "" and tg_userId != "":
            self.tgpush(f"爱奇艺每月领取会员\n{msg}")

    def print_now(self, content):
        print(content)
        stdout.flush()

    """获取用户会员等级"""

    def get_level(self):
        url = f'https://passport.iqiyi.com/apis/user/info.action?authcookie={self.ck}&fields=userinfo%2Cqiyi_vip&timeout=15000'
        data = self.req(url)
        if data.get("code") == 'A00000':
            self.level = data['data']['qiyi_vip_info']['level']
        else:
            self.print_now("获取用户等级信息失败 最大可能是cookie失效了 也可能是网络问题")
            exit(0)

    def genRedNo(self):
        url = f"https://act.vip.iqiyi.com/level-right/red/gen?fv=b75a9b2a7d208020&P00001={self.ck}"
        data = self.req(url)
        code = data.get("code")
        if code == "A00000":
            self.redNo = data["data"]["redNo"]
        elif code == "B000205":
            self.print_now("当前账号本月已领取等级红包 直接查询")
            self.query_redNo()

    def query_redNo(self):
        url = f"https://act.vip.iqiyi.com/level-right/red/status?fv=b75a9b2a7d208020&P00001={self.ck}"
        data = self.req(url)
        code = data.get("code")
        if code == "A00000":
            self.redNo = data["data"][0]["redNo"]

    def last_redNo(self, redNo):
        url = f"https://act.vip.iqiyi.com/bonus/query/queryRed?redNo={redNo}"
        data = self.req(url)
        if data.get("code") == "A00000":
            last_num = data["data"]["totalNum"] - data["data"]["receivedNum"]
            return last_num
        else:
            return 0

    def post_redNo(self):
        url = "https://api.ruirui.fun/iqiyi/postRedNo"
        body = {
            "RedNo": self.redNo,
            "last_num": self.last_num
        }
        req = post(url, json=body)
        if req.status_code == 200:
            data = req.json()
            if data.get("data") == "success":
                self.print_now("已将您的红包码提交到助力池")
                self.msg += "已将您的红包码提交到助力池"
            else:
                self.print_now(data["data"])
        else:
            self.print_now("提交失败, 可能为池子服务器炸了, 请截图运行时间和日志反馈")

    def get_redNo(self):
        url = "https://api.ruirui.fun/iqiyi/getRedNo"
        req = get(url)
        if req.status_code == 200:
            data = req.json()
            if data["msg"] == "success":
                redNo_list = data["data"]
            else:
                self.print_now("当前池子红包码为空")
                redNo_list = []
            return redNo_list
        else:
            self.print_now("从池子获取红包码失败, 可能为池子服务器炸了, 请携带日志反馈")
            exit(0)

    def receive(self, redNo):
        url = f"https://act.vip.iqiyi.com/bonus/api/grabRed?accountType=2&P00001={self.ck}&redNo={redNo}"
        data = self.req(url)
        code = data.get("code")
        if code == "A00000":
            receiveDay = data["data"]["receiveDays"]
            self.print_now(f"领取成功, 获得{receiveDay}天会员")
            self.msg += f"领取成功, 获得{receiveDay}天会员\n"
            return False
        else:
            self.print_now(f"领取失败 原因是{data['msg']}")
            if "上限" in data["msg"]:
                return True

    def main(self):
        self.get_level()
        if int(self.level) >= 5:
            self.genRedNo()
            if len(self.redNo) == 28:
                self.last_num = self.last_redNo(self.redNo)
                if self.last_num > 0:
                    self.print_now(f"您的红包码为{self.redNo}, 正在尝试提交")
                    self.post_redNo()
                else:
                    self.print_now(f"您本月的会员红包已被领完, 不提交")
        redNo_list = self.get_redNo()
        if len(self.redNo) == 28 and len(redNo_list) > 6:
            redNo_list.insert(0, self.redNo)
        self.print_now(f"本次获取到的红包码为\n{redNo_list}")
        for redNo in redNo_list:
            if redNo == "":
                continue
            status = self.receive(redNo)
            if status:
                break
            sleep(2)
        if self.msg == "":
            self.msg = "本次运行啥都没有得到"
        self.push(self.msg)


if __name__ == '__main__':
    iqiyi = Iqiyi(iqy_ck)
    iqiyi.main()
