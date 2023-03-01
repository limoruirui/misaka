<font size=5>只能说圈子开源风气太差了,不知道某些人什么心理,本仓库以后不会再进行维护,有缘也再也不见</font>
# misaka
- 随缘维护和上传, 请不要上传或者转载到其它地方。
- 本仓库脚本仅供用于学习及参考对应web/app的参数解密并提供对应demo用于测试,请不要询问如何多账号等
- 食用方法都在脚本内,请自行查看。
- 觉得好用可以点个star。
- 经反馈, 有部分社区使用本仓库内电信相关的测试demo进行二改牟利, 为避免纠纷, 本仓库删除相关测试demo。22.11.27
## 使用方法
### !!! 开发环境 windows10 python3 --version = 3.9.7
### !!! 部署运行环境 ubuntu 22.04.1 TLS  python3 --version = 3.8.10
### !!! 稍微测试过的环境 青龙面板 version = 2.12.2 & 2.10.6
### !!! 以上均为x86环境 arm环境未进行任何测试 以上环境遵照md均可正常运行, 请勿重复发与此相关的issue
### !!! 若遵照md的食用方法仍出问题, 请优先部署以上环境中的一个测试后 若仍有异常, 再带着详细说明提issue
### 一. ubuntu服务器
- 拉取整个仓库(部分文件可以单独跑)
  ```
  // 以下几条命令 请不要带着 $/# 一起复制 这两个符号只是代表了所需权限
  $ git clone https://github.com/limoruirui/misaka
- 安装依赖
  ```
  $ pip3 install -r requirements.txt
- 然后设置环境变量 以ubuntu为例 只提供参考
  ```
  $ sudo vim /etc/profile
  写入 export key="value" 多个环境变量就写入多行
- 执行脚本
  ```
  1.手动执行测试 在主目录下 执行
    $ python3 xxx.py >> logs/xxx.log
  2. crontab定时任务
    0 0 * * * . /etc/profile;cd 目录的绝对路径 && python3 xxx.py >> logs/xxx.log 2>&1
### 二. 青龙面板
- 拉取仓库
  ```
  ql repo https://github.com/limoruirui/misaka.git "" "backUp|tools|JS|logs|login"  "tools|JS|logs|login"
  国内服务器太卡的话用下面这个
  ql repo https://github.limoruirui.com/https://github.com/limoruirui/misaka.git "" "backUp|tools|JS|logs|login"  "tools|JS|logs|login"
- 安装依赖
  ```
  安装依赖时失败时 如果日志内有提示 gcc not found 的关键字 则进入docker容器中 依次执行
  $ apk update
  $ apk add build-base 
  此时在docker容器内执行 gcc --version 若正确显示版本信息 则可继续安装
  
  第一种方法: 在github复制requirements.txt内的所有东西 
  打开面板-依赖管理-新建依赖 依赖类型选 python3 自动拆分选 是 把复制的东西粘贴在名称内 确定即可
  
  第二种方法: 进入容器中 依次执行
  $ cd data/scripts/limoruirui_misaka
  $ wget https://raw.githubusercontent.com/limoruirui/misaka/master/requirements.txt
  $ pip3 install -r requirements.txt
- 按照脚本文件内的说明设置环境变量
## 常见异常说明
### 1. no module name "tools" 未按要求拉库 看md说明 根据自己环境拉
### 2. no module name "tools.xxx" 则将python3中的tools依赖删除
### 3. 运行时出现 sslError 之类的提示 则为自己网络问题
## 环境变量说明 
- 一.推送
  - 1.tgbot 
    - TG_USER_ID  tg用户id
    - TG_BOT_TOKEN tgbot的token
    - TG_API_HOST(可选, 若无或不需要则不设置) tg反向代理api
    - TG_BOT_TOKEN_ADDED (可选) 用于设置额外的tgbot的token 填写此变量后 则不会再去读取TG_BOT_TOKEN 当填写了TG_BOT_TOKEN 又不希望脚本使用tg推送时 则将TG_BOT_TOKEN_ADDED设置为 no
  - 2.pushplus
    - PUSH_PLUS_TOKEN 推送加的token
    - PUSH_PLUS_TOKEN_ADDED (可选) 同上面的TG_BOT_TOKEN_ADDED
- 二.脚本内变量 (**<big>具体参照脚本文件内的说明</big>**)
  - 1. 联通营业厅app(china_unicom.py)
    - PHONE_NUM 手机号码 (必须)
    - UNICOM_LOTTER 是否自动抽奖 (选填 True | False, 默认为是)
    - UNICOM_USERAGENT 联通的useragent (选填 具体的useragnet 抓包获得)
  - 2. 电信营业厅app(china_telecom.py)
    - TELECOM_PHONE 手机号码 (必须)
    - TELECOM_PASSWORD 电信服务密码 (选择)
    - TELECOM_FOOD 宠物喂食次数 (选择)
  - 3. iqiyi(iqiyi.py & iqiyiRed.py)
    - iqy_ck 爱奇艺cookie 可整段 也可只保留P00001=xxx; (必须)
    - get_iqiyi_dfp 是否请求我的api来获取参数 再去请求爱奇艺的api来获取dfp dfp类似于设备号 cookie字段内有 (选择 True | False 默认为否)
    - sleep_await 因观影时长同步有延迟 故建议完成任务后等待几分钟再查询 (选填 True | False 默认为是)
  - 4. 无忧行app(wxy.py)
    - WXY_TOKEN 无忧行app内的token (必须)
  - 5. 顺丰速运(sfexpress.py)
    - SF_SIGN 顺丰app的sign (必须)
## 文件目录说明
- 主目录 -- 存放主文件
- Tools -- 存放一些脚本内经常需要重复使用的工具
- JS -- 存放一些网站自己写的 过于复杂 不好使用python重写的加解密的js文件供python调用
- backUp -- 存放已经无法正常执行的文件
- logs -- 存放任务日志
## 特别声明

- 本仓库发布的脚本及其中涉及的任何解密分析脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。

- 本项目内所有资源文件，禁止任何公众号、自媒体进行任何形式的转载、发布。

- 本人对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害。

- 间接使用脚本的任何用户，包括但不限于建立VPS或在某些行为违反国家/地区法律或相关法规的情况下进行传播, 本人对于由此引起的任何隐私泄漏或其他后果概不负责。

- 请勿将本仓库的任何内容用于商业或非法目的，否则后果自负。

- 如果任何单位或个人认为该项目的脚本可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关脚本。

- 任何以任何方式查看此项目的人或直接或间接使用该项目的任何脚本的使用者都应仔细阅读此声明。本人保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或本项目的规则，则视为您已接受此免责声明。

**您必须在下载后的24小时内从计算机或手机中完全删除以上内容**
