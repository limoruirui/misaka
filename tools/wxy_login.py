#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/10/6 0:18
# -------------------------------
"""
无忧行账号密码登录获取token
1. 脚本仅供学习交流使用, 请在下载后24h内删除
2. 给无法抓包或者不会抓包的人使用 请先在app内设置密码 若登录后设置没有密码设置 先退出 再登录 找到密码登录 忘记密码
3. 环境变量说明 WXY_ACCOUNT_PWD(必需)
    WXY_ACCOUNT_PWD 账号&密码 账号密码用&连接 example: 12345678910&123456
"""
from requests import post
from tool import timestamp, md5, get_environ, sha1

wyx_account_info = get_environ("WXY_ACCOUNT_PWD")
if wyx_account_info == "":
    exit(0)
account_info = wyx_account_info.split("&")
account = account_info[0]
password = account_info[1]


def timestamp_to_arr(times):
    bArr = [0 for i in range(8)]
    for i in range(8):
        bArr[i] = ((times >> (64 - ((i + 1) << 3))) & 255)
    return bArr


def get_sign(times):
    bArr = [106, 117, 59, 58, 42, 99, 43, 40]
    bArr = bArr + timestamp_to_arr(times)
    sign = sha1(bArr)
    return sign


def get_sign_img_code(imgCodeToken, mobile, times):
    str = f"country_code=86&imgCodeToken={imgCodeToken}&mobile={mobile}&sign_key=wuyouxing&key&&timeStamp={times}&type=3"
    return sha1(str).upper()


def login_by_pwd():
    times = timestamp()
    url = f"https://app1.jegotrip.com.cn/api/user/v1/phoneUserLogin?n_token=&lang=zh_CN&timestamp={times}&sign={get_sign(times)}"
    body = {
        "countryCode": "86",
        "logintype": "2",
        "mobile": account,
        "password": md5(f"20150727*{password}")
    }
    data = post(url, json=body).json()
    if data["code"] == "0":
        print("您的token为(请直接复制使用): ")
        print(data["body"]["token"])
    else:
        print("登录失败, 登录接口返回的日志为: ")
        print(data)


if __name__ == "__main__":
    login_by_pwd()