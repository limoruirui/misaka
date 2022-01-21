# 本脚本是一个半成品 不可以直接使用 请先确认自己能抓到自己签到链接再折腾，避免浪费自己时间 签到链接格式如下 抓这个格式的就行 注意的是在正式发post包之前会有一个options预检包 这里面的链接应该也是能用的 ck过期则签到链接过期 理论上是三个月吧
# url = 'https://community.iqiyi.com/openApi/task/execute?agentType=1&agentversion=1&appKey=basic_pcw&authCookie=xxx&qyid=xxx&sign=xxx&task_code=natural_month_sign&timestamp=xxx&typeCode=point&userId=xxx'
# 本来前天就弄好了 不过一直在思考可行方案 不知道发什么形式的好 增加获取签到链接的api的最有效的 但也是争议性最大的 我服务器也承担被攻击风险 想来想去还是决定按现在这个方案走 自己抓
# 使用方式 直接下raw文件或者在自己机器上新建一个同名文件复制粘贴内容进去都可以 测试python3版本在3.6.x-3.8.x都可用 其它自测
# 本来不太想发的 sign逆向虽然弄出来了 但不确定开源出来会不会吃票 固定签到链接虽然能签到 但是后续会怎么样不能保证，请自行斟酌是否使用
# ck填写规则 只填写P00001的value值 如(P00001=xxx;的话 只填写xxx 不要P00001=) 会操作的话 库里有爱奇艺扫码获取P00001的脚本或者直接抓包软件抓
# 只写了tg推送 推送信息写在 24 25行处 若是能访问tg的机器会走tg原生接口 否则走饭袋api推送(参考温佬wenmoux的) 因为自己平常都是用tg推送 本来想加一个以前写过的pushplus 不过找不到代码放在哪里了 所以还是算了
# 本项目使用了第三方库requests 如果没安装报错请按报错信息执行，其它库均为py原生库
# 本人不使用青龙 但是青龙原理也是一样 单独下raw脚本 然后改脚本内容 不支持环境变量
# 后续大概可能应该也许不会更新什么了，医学生大五忙毕业了 最多加个上传ck自动获取签到链接的api 不过毕竟上传ck这种东西很敏感 而且我api服务器也可能会面临风险 所以可能也不弄 大家能抓到就用不会抓就等其它大佬更新一个更可行的方案
# 1.21更新 增加了一个上传ck获取自己号签到链接的api 默认为关闭状态 开启请在 29 行填open 上传ck有风险 有能力请自行抓包
# 本脚本仅供交流，请仔细斟酌得失再行使用，用户行为均与作者无关

try:
    from requests import post, get
except:
    print("你还没有安装requests库，请执行pip3 install requests安装后再执行")
from json import dumps
from hashlib import md5
from random import choice
from string import digits, ascii_lowercase
from base64 import b64decode

ck = ''
bot_token = ''
user_id = ''
url = ''
# 以下变量若设置为 open 则本脚本会将ck上传给api获取你自己的签到url 将打印出来的url填入 25 行的url里即可不用抓签到链接的包
mode = '' #默认为空，为正常执行签到 填入 open 执行脚本可获取签到链接 获取保存好之后请删除 open 否则不会进行签到任务

def main():
    data = {
  "natural_month_sign" : {
    "taskCode" : "iQIYI_mofhr",
    "agentType" : 1,
    "agentversion" : 1,
    "authCookie" : ck,
    "qyid" : md5Encode(uuid(16)),
    "verticalCode" : "iQIYI"
  }
}
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 IqiyiApp/iqiyi IqiyiVersion/12.11.5  IqiyiPlatform/2_22_221 WebVersion/QYWebContainer QYStyleModel/(dark)',
        'Content-Type':'application/json'
    }
    data = post(url, headers=headers, data=dumps(data)).json()
    print(data)
    if data['code'] == 'A00000':
        try:
            tgpush('今日签到成功或者已经签到了')
        except:
            print('你还没有填写tg推送信息或者网络问题')
        return '签到成功'
    else:
        return '签到失败，原因可能是签到接口又又又又改了'

def md5Encode(str): 
	m = md5(str.encode(encoding='utf-8'))
	return m.hexdigest()

def uuid(num):
    str = ''
    for i in range(num):
        str += choice(digits + ascii_lowercase)
    return str

def tgpush(content):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'chat_id': str(user_id), 'text': content, 'disable_web_page_preview': 'true'}
    try:
        req = post(url, headers=headers, data=data, timeout=10)
    except:
        print('推送失败,请检查网络问题')
def tgpush2(content):
    url = f"https://telegram_proxy.lulafun.workers.dev/bot{bot_token}/sendMessage?parse_mode=Markdown&text={content}&chat_id={user_id}"
    try:
        req = get(url, timeout=30)
    except:
        print('推送失败')

def getUrl():
    headers = {'Content-Type':'application/json'}
    data = {"ck":ck}
    return post(str(b64decode('aHR0cHM6Ly9zZXJ2aWNlLTA4aWlldTF3LTEzMDgxNDY3MTguZ3ouYXBpZ3cudGVuY2VudGNzLmNvbS9yZWxlYXNlL2dldHVybA==').decode()), headers=headers, data=dumps(data), timeout=20).json()['s']
if __name__ == '__main__':
    if mode == 'open':
	print(getUrl())
    else:
        main()
