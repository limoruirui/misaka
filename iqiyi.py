#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 5/5/2022 20:09
# -------------------------------
"""
1.爱奇艺每日任务脚本 请低调使用 请不要用于商业牟利
2.cookie获取方式
    1.cookie可以用别人loon、qx等软件的mitm类自动获取再去boxjs里复制出来填写到环境变量或本脚本中
    2.也可以自行抓包 电脑或者手机都可以
    3.实在都不会
3.cookie食用方式: 可以只保留P00001=xxx;中xxx的值 也可以整段都要 青龙运行可新建并放入到环境变量 iqy_ck 中 也可以直接填写在本脚本中
4.库中有每月自动领取爱奇艺会员天数红包的脚本 可配合使用(需有高等级的运行脚本提供红包 其它人才可以领取)
"""
cookie = ""
from time import sleep, time
from random import randint, choice
from json import dumps, loads
from hashlib import md5 as md5Encode
from string import digits, ascii_lowercase, ascii_uppercase
from sys import exit
from os import environ, system
from copy import deepcopy
from re import findall

try:
    from requests import Session
    from fake_useragent import UserAgent
except:
    print(
        "你还没有安装requests库和fake_useragent库 正在尝试自动安装 请在安装结束后重新执行此脚本\n若还是提示本条消息 请自行运行pip3 install requests和pip3 install fake-useragent或者在青龙的依赖管理里安装python的requests和fake-useragent")
    system("pip3 install fake-useragent")
    system("pip3 install requests")
    print("安装完成 脚本退出 请重新执行")
    exit(0)
iqy_ck = environ.get("iqy_ck") if environ.get("iqy_ck") else cookie
if iqy_ck == "":
    print("未填写cookie 青龙可在环境变量设置 iqy_ck 或者在本脚本文件上方将获取到的cookie填入cookie中")
    exit(0)
if "P00001" in iqy_ck:
    iqy_ck = findall(r"P00001=(.*?)(;|$)", iqy_ck)[0][0]


class Iqiyi:
    def __init__(self, ck):
        self.ck = ck
        self.session = Session()
        self.headers = {
            "User-Agent": UserAgent().chrome,
            "Cookie": f"P00001={self.ck}",
            "Content-Type": "application/json"
        }
        self.uid = ""
        self.msg = ""
        self.user_info = ""
        self.sleep_await = environ.get("sleep_await") if environ.get("sleep_await") else 1

    """工具"""

    def req(self, url, req_method="GET", body=None):
        data = {}
        if req_method.upper() == "GET":
            try:
                data = self.session.get(url, headers=self.headers, params=body).json()
            except:
                print("请求发送失败,可能为网络异常")
            #     data = self.session.get(url, headers=self.headers, params=body).text
            return data
        elif req_method.upper() == "POST":
            try:
                data = self.session.post(url, headers=self.headers, data=dumps(body)).json()
            except:
                print("请求发送失败,可能为网络异常")
            #     data = self.session.post(url, headers=self.headers, data=dumps(body)).text
            return data
        elif req_method.upper() == "OTHER":
            try:
                self.session.get(url, headers=self.headers, params=dumps(body))
            except:
                print("请求发送失败,可能为网络异常")
        else:
            print("您当前使用的请求方式有误,请检查")

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

    def get_userinfo(self):
        url = f"https://tc.vip.iqiyi.com/growthAgency/v2/growth-aggregation?messageId={self.qyid}&platform=97ae2982356f69d8&P00001={self.ck}&responseNodes=duration%2Cgrowth%2Cupgrade%2CviewTime%2CgrowthAnnualCard&_={self.timestamp()}"
        data = self.req(url)
        msg = data['data']['growth']
        try:
            self.user_info = f"查询成功: 到期时间{msg['deadline']}\t当前等级为{msg['level']}\n\t\t今日获得成长值{msg['todayGrowthValue']}\t总成长值{msg['growthvalue']}\t距离下一等级还差{msg['distance']}成长值"
            print(self.user_info)
        except:
            self.user_info = f"查询失败,未获取到用户信息"

    """获取用户id"""

    def getUid(self):
        url = f'https://passport.iqiyi.com/apis/user/info.action?authcookie={self.ck}&fields=userinfo%2Cqiyi_vip&timeout=15000'
        data = self.req(url)
        if data.get("code") == 'A00000':
            self.uid = data['data']['userinfo']['pru']
        else:
            print("请求api失败 可能是网络问题 也可能接口被玩坏了")
            exit(0)

    def get_sign(self):
        self.qyid = self.md5(self.uuid(16))
        time_stamp = self.timestamp()
        if self.uid == "":
            print("获取用户id失败 可能为cookie设置错误或者网络异常,请重试或者检查cookie")
            exit(0)
        data = f'agentType=1|agentversion=1|appKey=basic_pcw|authCookie={self.ck}|qyid={self.qyid}|task_code=natural_month_sign|timestamp={time_stamp}|typeCode=point|userId={self.uid}|UKobMjDMsDoScuWOfp6F'
        url = f'https://community.iqiyi.com/openApi/task/execute?agentType=1&agentversion=1&appKey=basic_pcw&authCookie={self.ck}&qyid={self.qyid}&sign={self.md5(data)}&task_code=natural_month_sign&timestamp={time_stamp}&typeCode=point&userId={self.uid}'
        return url

    def getUrl(self, Time, dfp):
        return f'https://msg.qy.net/b?u=f600a23f03c26507f5482e6828cfc6c5&pu={self.uid}&p1=1_10_101&v=5.2.66&ce={self.uuid(32)}&de=1616773143.1639632721.1639653680.29&c1=2&ve={self.uuid(32)}&ht=0&pt={randint(1000000000, 9999999999) / 1000000}&isdm=0&duby=0&ra=5&clt=&ps2=DIRECT&ps3=&ps4=&br=mozilla%2F5.0%20(windows%20nt%2010.0%3B%20win64%3B%20x64)%20applewebkit%2F537.36%20(khtml%2C%20like%20gecko)%20chrome%2F96.0.4664.110%20safari%2F537.36&mod=cn_s&purl=https%3A%2F%2Fwww.iqiyi.com%2Fv_1eldg8u3r08.html%3Fvfrm%3Dpcw_home%26vfrmblk%3D712211_cainizaizhui%26vfrmrst%3D712211_cainizaizhui_image1%26r_area%3Drec_you_like%26r_source%3D62%2540128%26bkt%3DMBA_PW_T3_53%26e%3Db3ec4e6c74812510c7719f7ecc8fbb0f%26stype%3D2&tmplt=2&ptid=01010031010000000000&os=window&nu=0&vfm=&coop=&ispre=0&videotp=0&drm=&plyrv=&rfr=https%3A%2F%2Fwww.iqiyi.com%2F&fatherid={randint(1000000000000000, 9999999999999999)}&stauto=1&algot=abr_v12-rl&vvfrom=&vfrmtp=1&pagev=playpage_adv_xb&engt=2&ldt=1&krv=1.1.85&wtmk=0&duration={randint(1000000, 9999999)}&bkt=&e=&stype=&r_area=&r_source=&s4={randint(100000, 999999)}_dianshiju_tbrb_image2&abtest=1707_B%2C1550_B&s3={randint(100000, 999999)}_dianshiju_tbrb&vbr={randint(100000, 999999)}&mft=0&ra1=2&wint=3&s2=pcw_home&bw=10&ntwk=18&dl={randint(10, 999)}.27999999999997&rn=0.{randint(1000000000000000, 9999999999999999)}&dfp={dfp}&stime={self.timestamp()}&r={randint(1000000000000000, 9999999999999999)}&hu=1&t=2&tm={Time}&_={self.timestamp()}'

    def sign(self):
        url = self.get_sign()
        body = {
            "natural_month_sign": {
                "taskCode": "iQIYI_mofhr",
                "agentType": 1,
                "agentversion": 1,
                "authCookie": self.ck,
                "qyid": self.qyid,
                "verticalCode": "iQIYI"
            }
        }
        data = self.req(url, "post", body)
        # print(data)
        if data.get('code') == 'A00000':
            print(f"签到执行成功, {data['data']['msg']}")
        else:
            print("签到失败，原因可能是签到接口又又又又改了")

    def dailyTask(self):
        taskcodeList = {'b6e688905d4e7184': "浏览生活福利",
                        'a7f02e895ccbf416': "看看热b榜",
                        '8ba31f70013989a8': "每日观影成就",
                        "freeGetVip": "浏览电信福利"}
        for taskcode in taskcodeList:
            # 领任务
            url = f'https://tc.vip.iqiyi.com/taskCenter/task/joinTask?P00001={self.ck}&taskCode={taskcode}&platform=b6c13e26323c537d&lang=zh_CN&app_lm=cn'
            if self.req(url)['code'] == 'A00000':
                # print(f'领取{taskcodeList[taskcode]}任务成功')
                sleep(10)
            # 完成任务
            url = f'https://tc.vip.iqiyi.com/taskCenter/task/notify?taskCode={taskcode}&P00001={self.ck}&platform=97ae2982356f69d8&lang=cn&bizSource=component_browse_timing_tasks&_={self.timestamp()}'
            if self.req(url)['code'] == 'A00000':
                # print(f'完成{taskcodeList[taskcode]}任务成功')
                sleep(2)
            # 领取奖励
            url = f'https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?P00001={self.ck}&taskCode={taskcode}&dfp=a168db20cec470441bac40a7052e573a18cf2190f6c78a1e946cc17450c9fc9b15&platform=b6c13e26323c537d&lang=zh_CN&app_lm=cn&deviceID={self.md5(self.uuid(8))}&token=&multiReward=1&fv=bed99b2cf5722bfe'
            price = self.req(url)['dataNew'][0]["value"]
            print(f"领取{taskcodeList[taskcode]}任务奖励成功, 获得{price}点成长值")
            sleep(5)

    def lottery_draw(self, lottery=True):
        """
        查询剩余抽奖次数和抽奖
        True 抽
        False 查
        """

        url = "https://iface2.iqiyi.com/aggregate/3.0/lottery_activity"
        lottery_params = {
            "app_k": "0",
            "app_v": "0",
            "platform_id": 10,
            "dev_os": "2.0.0",
            "dev_ua": "COL-AL10",
            "net_sts": 1,
            "qyid": self.qyid,
            "psp_uid": self.uid,
            "psp_cki": self.ck,
            "psp_status": 3,
            "secure_v": 1,
            "secure_p": "0",
            "req_sn": self.timestamp()
        }
        get_change_params = deepcopy(lottery_params)
        get_change_params["lottery_chance"] = 1
        params = get_change_params
        if lottery:
            params = lottery_params
        data = self.req(url, "get", params)
        if lottery and data.get("code") == 0:
            print(data["kv"]["msg"])
            return data["daysurpluschance"]
        elif not lottery and data.get("code") == 0:
            return data["daysurpluschance"]

    def start(self):
        print("正在执行刷观影时长脚本 为减少风控 本过程运行时间较长 大概半个小时")
        totalTime = 0
        for i in range(150):
            Time = randint(60, 120)
            dfp = self.uuid(66)
            url = self.getUrl(Time, dfp)
            self.req(url, 'other')
            totalTime += Time
            sleep(randint(20, 40))
            if totalTime >= 7600:
                break

    def main(self):
        self.getUid()
        self.get_sign()
        self.start()
        for i in range(10):
            change = self.lottery_draw()
            if int(change) == 0:
                break
            sleep(3)
        self.sign()
        self.dailyTask()
        print(f"任务已经执行完成, 因爱奇艺观影时间同步较慢,这里等待3分钟再查询今日成长值信息,若不需要等待直接查询,请设置环境变量名 sleep_await = 0 默认为等待")
        if int(self.sleep_await) == 1:
            sleep(180)
        self.get_userinfo()


if __name__ == '__main__':
    iqiyi = Iqiyi(iqy_ck)
    iqiyi.main()
