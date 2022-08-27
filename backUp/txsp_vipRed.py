#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 22/5/2022 10:48
# -------------------------------

"""
1.腾讯视频每月领取会员天数红包 请低调使用 请不要用于商业牟利
2.活动时间为每个月的 8号到13号 的 10点到24点
3.活动期间内一天一次 每天限制领取两次 每个月限制次数暂时未知 请自行探索 请自行斟酌crontab
4.cookie获取方式
    1.cookie可以用别人loon、qx等软件的mitm类自动获取再去boxjs里复制出来填写到环境变量或本脚本中
    2.也可以自行抓包 电脑或者手机都可以 抓链接为https://access.video.qq.com/user/auth_refresh?的 要整段url和对应headers下的cookie
5.cookie食用方式: cookie和url都要整段 青龙运行可新建并分别放入到环境变量 V_COOKIE和V_REF_URL 中
6.推荐抓取腾讯视频app端随便一条链接的headers下的user-agent 并放入环境变量 TX_UA 中 不填写会使用随机的chrome浏览器的user-agent
7.推送支持tgbot和pushplus 会读取环境变量 青龙若之前有设置 则不需要额外设置
"""
from random import randint
from time import time, sleep
from re import findall
from os import environ, system
from sys import exit, stdout
from json import dumps, load
from datetime import datetime

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


class Txsp_vipRed:
    def __init__(self):
        self.cookie = environ.get("V_COOKIE")
        self.ref_url = environ.get("V_REF_URL")
        if self.cookie == "" or self.ref_url == "":
            self.print_now("未填写腾讯V_COOKIE或者V_REF_URL")
            exit(0)

        self.msg = ""
        self.actId = ""
        self.laisee_id = ""
        self.session = Session()
        self.ua = environ.get("TX_UA") if environ.get("TX_UA") else UserAgent().chrome
        self.own_ex = environ.get("TX_EGG_OWN") if environ.get("TX_EGG_OWN") else False
        self.headers = {
            "user-agent": self.ua
        }

        """推送相关"""
        self.pushplus_token = environ.get("PUSH_PLUS_TOKEN") if environ.get("PUSH_PLUS_TOKEN") else ""
        self.tgbot_token = environ.get("TG_BOT_TOKEN") if environ.get("TG_BOT_TOKEN") else ""
        self.tg_userId = environ.get("TG_USER_ID") if environ.get("TG_USER_ID") else ""
        self.tg_push_api = environ.get("TG_API_HOST") if environ.get("TG_API_HOST") else ""

    """工具"""

    def pushplus(self, title, content):
        url = "http://www.pushplus.plus/send"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "token": self.pushplus_token,
            "title": title,
            "content": content
        }
        try:
            post(url, headers=headers, data=dumps(data))
        except:
            self.print_now('推送失败')

    def tgpush(self, content):
        url = f"https://api.telegram.org/bot{self.tgbot_token}/sendMessage"
        if self.tg_push_api != "":
            url = f"https://{self.tg_push_api}/bot{self.tgbot_token}/sendMessage"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'chat_id': str(self.tg_userId), 'text': content, 'disable_web_page_preview': 'true'}
        try:
            post(url, headers=headers, data=data, timeout=10)
        except:
            self.print_now('推送失败')

    def push(self, msg):
        if self.pushplus_token != "":
            self.pushplus("腾讯视频每月领取会员", msg)
        if self.tgbot_token != "" and self.tg_userId != "":
            self.tgpush(f"腾讯视频每月领取会员\n{msg}")

    def timestamp(self, short=False):
        if (short):
            return int(time())
        return int(time() * 1000)

    def print_now(self, content):
        print(content)
        stdout.flush()

    """重置cookie有效期"""

    def refresh_cookie(self):
        headers = {
            'Referer': 'https://v.qq.com',
            "Cookie": self.cookie,
            "User-Agent": self.ua
        }
        req = self.session.get(self.ref_url, headers=headers)
        if req.headers.get("Set-Cookie") == None:
            if self.pushplus_token != "":
                self.pushplus("腾讯视频碰蛋活动", "cookie过期或填写错误")
            if self.tgbot_token != "" and self.tg_userId != "":
                self.tgpush(f"腾讯视频碰蛋活动\ncookie过期或填写错误")
            self.print_now("cookie过期或者填写错误, 退出")
            exit(0)
        # data = loads(req.text[42:-2])
        data = req.text
        # self.head = data["head"]
        # self.nickname = data["nick"]
        self.head = findall(r"\"head\":\"(.*?)\"", data)[0]
        self.nickname = findall(r"\"nick\":\"(.*?)\"", data)[0]

    def get_laisee_id(self):
        url = "https://api.ruirui.fun/txsp/get_laisee_id"
        try:
            data = get(url).json()
            if data.get("msg") == "success":
                self.print_now(f"获取到的助力码为{data['data']}")
                return data["data"]
            else:
                self.print_now("从获取助力码失败,最大可能是助力池为空")
                self.msg += "本次运行没有获取到红包码, 可能是池子为空"
                return False
        except:
            self.print_now("获取助力码失败, 可能是api炸了, 也可能你的网络有问题")
            return False

    def post_laisee_id(self, laisee_id):
        url = "https://api.ruirui.fun/txsp/post_laisee_id"
        body = {
            "laisee_id": laisee_id,
            "last_num": self.lastnum
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            data = post(url, headers=headers, json=body).json()
            if data.get("data") == "success":
                self.msg += "互助码提交成功"
                self.print_now("互助码提交成功")
        except:
            self.print_now("互助码提交失败,跳过提交,获取助力码")

    def get_level(self):
        url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=payvip&cmd=1&otype=json&getannual=1&geticon=1&getsvip=1&g_tk=610014353&_={self.timestamp()}&callback=Zepto{self.timestamp()}'
        headers = {
            "referer": "https://film.qq.com/x/autovue/grade/?ptag=user.h5",
            "host": "vip.video.qq.com",
            "accept-encoding": "gzip, deflate, br",
            "user-agent": self.ua}
        response = self.session.get(url=url, headers=headers)
        response.encoding = "utf-8"
        try:
            level = response.text.split('level')[1].split(',')[0].split(':')[1]
            return level
        except:
            self.print_now("获取等级信息失败, 最大可能是cookie过期或者格式不对, 也可能为网络原因")
            exit(0)

    def getActId(self):
        url = 'https://film.qq.com/x/autovue/privilege/?pid=privilege&hidetitlebar=1&hidestatusbar=0&style=titlecolor%3D%23ffffff%26contentbkcolor%3D%23fdf6e2&aid=V0$$1:0$2:7$3:8.4.77.25550$4:0$8:4$12:&isDarkMode=0&uiType=MAX'
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/11A465 QQLiveBrowser /8.4.55 AppType/UN WebKitCore/WKWebView iOS GDTTangramMobSDK/4.370.6 GDTMobSDK/4.370.6 cellPhone/iPad 1G'
        }
        req = self.session.get(url, headers=headers)
        req.encoding = 'utf-8'
        actId = findall(r'"laiSeeActId":"(.*?)",', req.text)[0]
        if len(actId) == 26:
            return actId
        else:
            self.msg += '活动id获取失败，请检查'
            return None

    def check_lastnum(self, laisee_id):
        url = f"https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_vipred_route_read&cmd=1&laisee_id={laisee_id}&otype=xjson&_ts={self.timestamp()}"
        headers = {
            "Referer": f"https://m.film.qq.com/magic-act/{self.actId}/index_index.html?ovscroll=0&page=index&isDarkMode=0&uiType=MAX",
            "User-Agent": self.ua
        }
        data = get(url, headers=headers).json()
        self.lastnum = int(data["total"]) - int(data["used"])
        if self.lastnum == 0:
            self.print_now("您本月的红包已被领完,暂不提交")
            return False
        return True

    def gen_laisee_id(self, actId):
        url = f'https://vip.video.qq.com/rpc/trpc.vip_red_group.vip_red_qualification.VipRedQualification/RedQualificationSend?rpc_data=%7B%22act_id%22:%22{actId}%22%7D'
        headers = {
            'User-Agent': self.ua,
            'Referer': 'https://film.qq.com/x/autovue/privilege/route/homepage/take?pid=privilege&hidetitlebar=1&hidestatusbar=0&style=titlecolor%3D%23ffffff%26contentbkcolor%3D%23fdf6e2&aid=V0%24%241%3A0%242%3A7%243%3A8.4.77.25550%244%3A0%248%3A4%2412%3A&isDarkMode=0&uiType=MAX'
        }
        data = self.session.get(url, headers=headers).json()
        order_id = data['orderid']
        # print(order_id)
        url2 = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?callback=jQuery{randint(30000000000000000000, 39999999999999999999)}_{self.timestamp()}&name=spp_vipred_route_write&cmd=1&head={self.head}&nick={self.nickname}&order_id={order_id}&_={self.timestamp()}'
        # print(url2)
        data = self.session.get(url2, headers=headers).text
        self.print_now(data)
        try:
            self.laisee_id = findall(r'"laisee_id":"(.*?)",', data)[0]
        except:
            self.print_now("生成红包码失败, 可能是今天已经领完了, 请明天早上10点再来")
            self.laisee_id = ""
        if self.laisee_id != "":
            self.msg += f"腾讯视频红包分享链接,https://m.film.qq.com/magic-act/{actId}/1_index_index.html?ptag=redshare&redenvelopeId={self.laisee_id}&ovscroll=0&page=index  点击链接领取几天腾讯视频会员"
            return True
        else:
            return False

    def receive(self, laisee_id):
        url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_vipred_route_write&cmd=2&laisee_id={laisee_id}&nick={self.nickname}&head={self.head}&act_id={self.actId}&otype=xjson&_ts={self.timestamp()}'
        headers = {
            'Origin': 'https://m.film.qq.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'vip.video.qq.com',
            'User-Agent': self.ua,
            'Referer': f'https://m.film.qq.com/magic-act/{self.actId}/index_index.html?ovscroll=0&page=index&isDarkMode=0&uiType=MAX'
        }
        data = self.session.get(url, headers=headers).json()
        self.print_now(data)
        if "content" in data:
            receive_day = data["content"]
            self.print_now(f"领取成功, 获得{receive_day}天会员, 也可能是这个月已经领过的")
            self.msg += f"领取成功, 获得{receive_day}天会员, 也可能是这个月已经领过的"
            sleep(1)
        else:
            self.print_now("领取失败,此红包码已被领完或者你本日/本周/本月已领到上限")

    def main(self):
        today = datetime.today().day
        hour = datetime.today().hour
        if today < 8 or today > 13 or hour < 10:
            self.print_now("当前不在活动时间 活动时间为每个月的8号到13号的10点到24点")
            exit(0)
        self.refresh_cookie()
        self.actId = self.getActId()
        if self.actId is None:
            self.print_now(self.msg)
            self.push(self.msg)
            exit(0)
        if int(self.get_level()) >= 6:
            self.print_now("您当前账号大于等于6级, 领取红包码并分享")
            if self.gen_laisee_id(self.actId):
                if self.check_lastnum(self.laisee_id):
                    self.post_laisee_id(self.laisee_id)
        laisee_id_list = self.get_laisee_id()
        if laisee_id_list:
            self.print_now(f"本次获取到的红包码为\n{laisee_id_list}")
            for laisee_id in laisee_id_list:
                self.receive(laisee_id)
        self.push(self.msg)

if __name__ == '__main__':
    Txsp_vipRed().main()
    # test = Txsp_vipRed()
    # test.gen_laisee_id(actId="6iuw8rky3tsid022s4rf5iauqg")
