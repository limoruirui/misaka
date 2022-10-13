#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/8/23 23:31
# -------------------------------
from requests import post
from json import dumps
from sys import path
path.append("./tools")
from tool import get_environ

tg_userId = get_environ("TG_USER_ID", "", False)
tgbot_token = get_environ("TG_BOT_TOKEN_ADDED", "", False) if get_environ("TG_BOT_TOKEN_ADDED", "", False) else get_environ("TG_BOT_TOKEN", "", False)
tg_push_api = get_environ("TG_API_HOST", "", False)
pushplus_token = get_environ("PUSH_PLUS_TOKEN_ADDED", "", False) if get_environ("PUSH_PLUS_TOKEN_ADDED", "", False) else get_environ("PUSH_PLUS_TOKEN", "", False)

def tgpush(title, content):
    url = f"https://api.telegram.org/bot{tgbot_token}/sendMessage"
    if tg_push_api != "":
        url = f"https://{tg_push_api}/bot{tgbot_token}/sendMessage"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'chat_id': str(tg_userId), 'text': f"{title}\n{content}", 'disable_web_page_preview': 'true'}
    try:
        post(url, headers=headers, data=data, timeout=10)
    except:
        print('推送失败')
def pushplus(title, content):
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
def push(title, content):
    if pushplus_token != "" and pushplus_token != "no":
        pushplus(title, content)
    if tgbot_token != "" and tgbot_token != "no" and tg_userId != "":
        tgpush(title, content)