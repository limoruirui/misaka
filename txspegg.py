#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 7/5/2022 20:48
# -------------------------------
"""
1.腾讯视频碰蛋活动 请低调使用 请不要用于商业牟利
2.一天一次或者两次(推荐一次) (((若在每天的16点后运行且环境变量 TX_EGG_OWN 设置为true 则会自己的账号单独开一次(个人不是很建议这种做法 不找人碰不确定会不会加大黑号风险 请自行斟酌),)))
    括号内的时间和变量必须同时满足才会自己碰自己 否则都是池子有码就碰池子 没有就上传你的码到池子 请自行斟酌设置crontab
3.cookie获取方式
    1.cookie可以用别人loon、qx等软件的mitm类自动获取再去boxjs里复制出来填写到环境变量或本脚本中
    2.也可以自行抓包 电脑或者手机都可以 抓链接为https://access.video.qq.com/user/auth_refresh?的 要整段url和对应headers下的cookie
4.cookie食用方式: cookie和url都要整段 青龙运行可新建并分别放入到环境变量 V_COOKIE和V_REF_URL 中
5.推荐抓取腾讯视频app端随便一条链接的headers下的user-agent 并放入环境变量 TX_UA 中 不填写会使用随机的chrome浏览器的user-agent
6.推送支持tgbot和pushplus 会读取环境变量 青龙若之前有设置 则不需要额外设置
"""
from time import time, sleep, localtime
from re import findall
from os import environ, system
from sys import exit, stdout
from json import dumps

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


class Txspegg:
    def __init__(self):
        self.cookie = environ.get("V_COOKIE")
        self.ref_url = environ.get("V_REF_URL")
        if self.cookie == "" or self.ref_url == "":
            self.print_now("未填写腾讯V_COOKIE或者V_REF_URL")
            exit(0)

        self.msg = ""
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

    """碰了别人的则上报别人的次数+1 用于计数别人的蛋有没有碰完 暂时未使用 后续观察情况再说"""
    def egg_sharecode_success(self, sharecode):
        url = "https://api.ruirui.fun/txsp/egg_success"
        body = {
            "sharecode": sharecode
        }
        try:
            post(url, json=body)
        except:
            self.print_now("上报失败")

    def get_egg_sharecode(self):
        url = "https://api.ruirui.fun/txsp/get_egg_sharecode"
        try:
            data = get(url).json()
            if data.get("msg") == "success":
                self.print_now(f"获取到的助力码为{data['data']}")
                return data["data"]
            else:
                self.print_now("从获取助力码失败,最大可能是助力池为空, 会尝试将您的助力码提交到池中")
                return False
        except:
            self.print_now("获取助力码失败, 可能是api炸了, 也可能你的网络有问题")
            return False

    def post_sharecode(self):
        url = "https://api.ruirui.fun/txsp/post_egg_sharecode"
        body = {
            "sharecode": self.get_sharecode()
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

    def get_sharecode(self):
        url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=spp_fulishe_eggs_collision&cmd=65391&actid=flspd_com&_st={self.timestamp()}'
        headers = {
            'User-Agent': self.ua,
            'Referer': 'https://film.qq.com/act/d2d-welfare/index.html?showMission=1&ptag=fuli.xrk&isDarkMode=0&uiType=MAX'
        }
        share_code = self.session.get(url, headers=headers).json()['data']['share_code']
        return share_code

    def get_egg(self):
        url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=fulishe_eggs_adapter&cmd=1&actid=flspd_com&_st={self.timestamp()}'
        headers = {
            'User-Agent': self.ua,
            'Referer': 'https://film.qq.com/act/d2d-welfare/index.html?showMission=1&ptag=fuli.xrk&isDarkMode=0&uiType=MAX'
        }
        self.session.get(url, headers=headers)

    def get_egg_count(self):
        url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=spp_fulishe_eggs_index&cmd=2&actid=flspd_com&_st={self.timestamp()}'
        headers = {
            'User-Agent': self.ua,
            'Referer': 'https://film.qq.com/act/d2d-welfare/index.html?showMission=1&ptag=fuli.xrk&isDarkMode=0&uiType=MAX'
        }

        return self.session.get(url, headers=headers).json()['data']['egg_count']

    def together(self, share_code):
        url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=spp_fulishe_eggs_collision&cmd=65394&share_code={share_code}&_st={self.timestamp()}'
        headers = {
            'User-Agent': self.ua,
            'Referer': 'https://film.qq.com/act/d2d-welfare/index.html?showMission=1&ptag=fuli.xrk&isDarkMode=0&uiType=MAX'
        }
        data = self.session.get(url, headers=headers).json()
        if data['ret'] == -1019:
            self.print_now('您已经和他碰过了')
            return ""
        if data['ret'] == -1016:
            self.print_now('他已经没有蛋蛋了')
            return ""
        if data['ret'] == -1017:
            self.print_now('你已经没有蛋蛋了')
            return ""
        if data['ret'] == 0:
            try:
                own = data['data']['guest_lottery_info']['property_name']
                guest = data['data']['master_lottery_info']['property_name']
                result = f'你得到了{own}, 对方得到了{guest}'
                # self.egg_sharecode_success(share_code)
                self.print_now(result)
                self.msg += f'{result}\n'
            except:
                self.tgpush(data)

    def own(self):
        own_url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=json&name=spp_fulishe_eggs_collision&cmd=65395&actid=flspd_com&_={self.timestamp()}&callback=Zepto{self.timestamp()}'
        headers = {
            'User-Agent': self.ua,
            'Referer': 'https://film.qq.com/act/d2d-welfare/index.html?showMission=1&ptag=fuli.xrk&isDarkMode=0&uiType=MAX'
        }
        html_data = self.session.get(own_url, headers=headers).text
        try:
            data = findall(r'"property_name":"(.*?)","property_result"', html_data)[0]
            self.msg += f'你得到了{data}'
        except:
            self.print_now("自己碰自己失败 可能为网络问题")

    def main(self):
        self.refresh_cookie()
        if int(self.get_level()) < 1:
            self.print_now("您当前账号不是腾讯视频会员, 无法参与")
            exit(0)
        if self.own_ex and localtime().tm_hour == 16:
            self.own()
        else:
            self.get_egg()
            sharecode_list = self.get_egg_sharecode()
            if sharecode_list != False:
                for sharecode in sharecode_list:
                    if int(self.get_egg_count()) == 0:
                        self.print_now("你已经没有蛋蛋了, 退出执行")
                        self.msg = "你没有蛋蛋了"
                        break
                    self.together(sharecode)
                    sleep(2)
            if int(self.get_egg_count()) > 0:
                self.post_sharecode()
            if self.msg == "互助码提交成功":
                self.msg += "\n本次执行没有碰到任何蛋,但是成功将互助码提交到了互助池,等待其它人碰即可"
            if self.msg == "":
                self.msg = "本次执行既没有碰到别人的蛋 也没能将您的助力码提交到池子 可能为池子服务器问题或者网络原因 请尝试重新提交"
            if self.pushplus_token != "":
                self.pushplus("腾讯视频碰蛋活动", self.msg)
            if self.tgbot_token != "" and self.tg_userId != "":
                self.tgpush(f"腾讯视频碰蛋活动\n{self.msg}")

if __name__ == '__main__':
    Txspegg().main()
