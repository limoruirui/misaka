#1 腾讯视频会员自动碰蛋，会员等级6级和6级以下每天两个蛋，7、8级每天三个
#2 每个号每天可以跟同一个人碰一次（包括自己），因为写的时候没什么人想要
#，就没弄助力池的形式，使用此脚本默认每个号自己跟自己碰一次，如果自己有几个号，
#可以适当修改本脚本使用，94行为自己碰自己，95行为根据自己填写ck获取互助码，内部互助，后续的若使用者增多考虑改为助力池形式
#3 ck参数同腾讯视频签到，自己找其它库看ck获取方法，填在25和26行中，ck单账号格式['xxx'],
# 多账号格式['xxx','yyy','zzz'] 外面的中括号 里面的单引号 逗号都不能省略
#4 只写了tg推送，参数在14 15行，不需要推送留空即可
from requests import get, post
from time import time
from copy import deepcopy
from re import findall
share_code_pool = []
def tgpush(content):
    bot_token = ''
    user_id = ''
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'chat_id': str(user_id), 'text': content, 'disable_web_page_preview': 'true'}
    try:
        req = post(url, headers=headers, data=data)
    except:
        print('推送失败,可能为网络问题或未配置tgbot')
def timestamp():
    return(int(round(time()*1000)))
def login():
    cookie_list = []
    ck_list =[]
    ref_url_list = []
    login_list = zip(ref_url_list, ck_list)
    for ref_url, ck in login_list:
        headers_resetck = {
     'Referer': 'https://v.qq.com',
     "Cookie":ck,
     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15" 
    }
        faul_num = 3
        while faul_num > 0:
            try:
                req = get(ref_url,headers=headers_resetck)
                if req.status_code == 200:
                    try:
                        vqq_vusession = req.headers['Set-Cookie'].split('vqq_vusession=')[1].split(';')[0]
                    except:
                        faul_num -= 1
                        continue
                    try:
                        cookie = ck.split('vqq_vusession=')[0] + f'vqq_vusession={vqq_vusession};' + ck.split('vqq_vusession=')[1].split(';', 1)[1]
                    except:
                        print('每日更新ck失败，可能为ref_url或者ck填写错误，请检查')
                    cookie_list.append(cookie)
                    break
            except:
                faul_num -= 1
                continue
    return cookie_list
def get_sharecode(ck):
    url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=spp_fulishe_eggs_collision&cmd=65391&actid=flspd_com&_st={timestamp()}'
    headers = {
      'Referer': 'https://film.qq.com/act/d2d-welfare/index.html',
      'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/19A346 QQ/8.8.33.634 V1_IPH_SQ_8.8.33_1_APP_A Pixel/1668 MiniAppEnable SimpleUISwitch/0 StudyMode/0 CurrentMode/0 CurrentFontScale/1.000000 QQTheme/1000 Core/WKWebView Device/Apple(Unknown iPad) NetType/WIFI QBWebViewType/1 WKType/1',
      'Cookie':ck
    }
    share_code = (get(url, headers=headers).json()['data']['share_code'])
    share_code_pool.append(share_code)
    return share_code_pool
def start():
    ck_list= login()
    account_numb = 0
    for ck in ck_list:
        share_code_list = get_sharecode(ck)
        try_url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=fulishe_eggs_adapter&cmd=1&actid=flspd_com&_st={timestamp()}'
        headers = {
       'Cookie':ck,
       'Referer': 'https://film.qq.com/act/d2d-welfare/index.html'
    }
        data = get(try_url, headers=headers).text
        try:
            tgpush(data)
        except:
            print('tg推送通知失败，可能为参数未填写或没有国外访问环境')
    for ck in ck_list:
        headers1 = {
       'Cookie':ck,
       'Referer': 'https://film.qq.com/act/d2d-welfare/index.html'
    }
        run_share_code_list = deepcopy(share_code_list)
        del run_share_code_list[account_numb]
        account_numb += 1
        for share_code in run_share_code_list:
            url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=spp_fulishe_eggs_collision&cmd=65394&share_code={share_code}&_st={timestamp()}'
            lishi_url1 = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=xjson&name=spp_fulishe_eggs_index&cmd=5&actid=flspd_com&_st={timestamp()}'
            #自己碰自己
            own_url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?otype=json&name=spp_fulishe_eggs_collision&cmd=65395&actid=flspd_com&_={timestamp()}&callback=Zepto{timestamp()}'
            html_data = get(own_url, headers=headers1).text
            #html_data = get(url, headers=headers1).text
            data = findall(r'"property_name":"(.*?)","property_result"', html_data)
            try:
                tgpush(data)
            except:
                print('tg推送通知失败，可能为参数未填写或没有国外访问环境')
if __name__ == '__main__':
    start()
