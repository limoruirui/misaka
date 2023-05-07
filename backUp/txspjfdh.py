# !!!!!此脚本应该已不可用,更新了 需要逆向解密参数 没什么收益 懒得更新了 需要更新的话提issue再说吧
#腾讯视频积分兑换任务，9积分换10成长值，一周一次（别问为什么写，问就是写完之前不知道是一周一次）
#ck用签到ck，获取方法其它腾讯视频签到库有，两个参数分别填在33 34行内，多账号格式['xxx', 'yyy', 'zzz']
#tg推送改15 16行参数
from requests import get, post
from random import choice
from time import time
from re import findall
def get_ua(brower_name):
    url = 'https://raw.githubusercontent.com/limoruirui/misaka/master/user-agent.json'
    useragent = choice(get(url).json()[brower_name])
    return useragent
def timestamp():
    return int(round(time()*1000))
def tgpush(content):
    bot_token = ''
    user_id = ''
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'chat_id': str(user_id), 'text': content, 'disable_web_page_preview': 'true'}
    try:
        req = post(url, headers=headers, data=data)
    except:
        print('推送失败')
def get_headers(ck, ua, Referer):
    headers = {
      'Cookie':ck,
      'User-Agent':ua,
'Referer': Referer
    }
    return headers
def login():
    cookie_list = []
    ref_url_list = ['']
    ck_list = ['']
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
                    cookie = ck.split('vqq_vusession=')[0] + f'vqq_vusession={vqq_vusession};' + ck.split('vqq_vusession=')[1].split(';', 1)[1]
                    cookie_list.append(cookie)
                    break
            except:
                continue
    #return cookie_list[int(argv[1])]
    return cookie_list
def jfye(ck, ua):
    url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=get_cscore&type=1&_={timestamp()}&callback=Zepto{timestamp()}'
    headers = {
      'Cookie':ck,
      'User-Agent':ua,
'Referer': 'https://film.qq.com/x/credit_mall/route/creditDetail?ptag=hlw.vmallscore'
    }
    jfye = findall(r'"vip_score_total":(.*?),', get(url, headers=headers).text)[0]
    return jfye
def get_9list():
    for i in range(0, 3):
        url = 'https://film.qq.com/x/credit_mall/cgi/productListByModule?_param=%7B%22moduleId%22%3A%2220200710006728%22%2C%22page%22%3A1%2C%22page_size%22%3A15%7D'
        shop_data = get(url).json()['data'][i]
        if shop_data['uiRealCreditPrice'] <= 10:
            sProductId = shop_data['sProductId']
            return sProductId
        else:
            continue
    tgpush('本次运行未发现积分低于10的物品')
def get_billno(ck, ua):
    url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=welfare_donate&g_vstk=1376497764&g_actk=3899139375&aid=V0%24%242%3A5%2412%3Ahlw.vmallscore%243%3A8.4.90%2434%3A1%248%3A4101&welfare_id={get_9list()}&score=1&remark=&_={timestamp()}&callback=Zepto{timestamp()}'
    Referer = f'https://film.qq.com/x/credit_mall/route/productDetail?productId={get_9list()}&ptag=hlw.vmallscore'
    billno = findall(r'"bill_no":"(.*?)",', get(url, headers=get_headers(ck, ua, Referer)).text)[0]
    return billno
def exchange(ck, ua):
    url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=scores_exchange&cmd=61232&source=101&bill_no={get_billno(ck, ua)}&productid={get_9list()}&price=9&aid=V0%24%242%3A5%244%3A0%2412%3Ahlw.vmallscore%248%3A999%243%3A8.4.60%241%3A0%2434%3A1%248%3A4002&_={timestamp()}&callback=Zepto{timestamp()}'
    Referer = f'https://film.qq.com/x/credit_mall/route/productDetail?productId={get_9list()}&ptag=hlw.vmallscore'
    get(url, headers=get_headers(ck, ua, Referer))
    print(f'您当前拥有{jfye(ck, ua)}积分')
def lingqu(ck, ua, account_numb):
    url = f'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_MissionFaHuo&cmd=4&task_id=8&_={timestamp()}&callback=Zepto{timestamp()}'
    Referer = 'https://v.qq.com'
    try:
        data = get(url, headers=get_headers(ck, ua, Referer)).text
        score = findall(r'"score":(.*?)}', data)[0]
        if score != 0:
            account_numb += 1
    except:
        print('周任务-积分兑换完成失败')
    return data
def main():
    ck_list = login()
    account_numb = 0
    for ck in ck_list:
        ua = get_ua('Safari')
        data = lingqu(ck, ua, account_numb)
        if '已发过货' in data:
            print('此账号本周已领取，请下周再来')
            account_numb += 1
        elif '"score":' in data:
            print('领取成功')
        else:
            exchange(ck, ua)
            lingqu(ck, ua, account_numb)
    tgpush(f'本次运行周任务-积分兑换成功完成{account_numb}个账号')
if __name__ == '__main__':
    main()
