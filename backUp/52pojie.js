/*
-- coding: utf-8 --
-------------------------------
@Author : github@limoruirui https://github.com/limoruirui/misaka
@Time : 24/7/2022 00:14
-------------------------------*/
/*
* 1. 浏览器打开抓包 https://www.52pojie.cn/home.php?mod=spacecp&ac=credit&showcredit=1
* 2. 将获取到的cookie整段填入15行中 或者填入boxjs中 变量名POJIE_COOKIE
* 3. 只测试了Loon 其它自测 crontab 自选
*     [Script]
*       cron "13 13 * * *" script-path=https://raw.githubusercontent.com/limoruirui/misaka/master/52pojie.js, tag=52破解签到
* 4. 脚本有风险,使用需谨慎.*/
//若要将cookie填在脚本里 请填在下面这行
let pojie_cookie = "";
const $ = API("52破解签到");
pojie_cookie = pojie_cookie || $.read("POJIE_COOKIE");
const chrome_version_min = 89;
const chrome_version_max = 103;
const chrome_version = Math.floor(Math.random() * (chrome_version_max - chrome_version_min)) + chrome_version_min;
const headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": pojie_cookie,
    "Host": "www.52pojie.cn",
    "Content-Type": "text/plain;charset=UTF-8",
    "Pragma": "no-cache",
    "sec-ch-ua": `".Not/A)Brand";v="99", "Google Chrome";v="${chrome_version}", "Chromium";v="${chrome_version}"`,
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${chrome_version}.0.${Math.floor(Math.random() * (999 - 100)) + 100}.${Math.floor(Math.random() * (99 - 10)) + 10} Safari/537.36`
};
if (pojie_cookie.length === 0) {
    $.notify("52破解", "", "cookie为空, 请检查");
} else {
    (async () => {
        await get_task();
        //接任务后等待两秒钟后再执行
        await $.wait(2000);
        await check_in();
        $.done();
    })();
}

function get_task() {
    let get_task_req_data = {
        url: "https://www.52pojie.cn/home.php?mod=task&do=apply&id=2",
        headers: headers
    }
    $.http.put(get_task_req_data)
}

async function check_in() {
    let check_in_data = {
        url: "https://www.52pojie.cn/home.php?mod=task&do=draw&id=2&referer=https%3A%2F%2Fwww.52pojie.cn%2F.%2F%2Fthread-1521480-1-1.html",
        headers: headers
    }
    let req = await $.http.put(check_in_data);
    if (req.body.indexOf("您需要先登录才能继续本操作") !== -1) {
        $.notify("52破解", "", "cookie失效, 请检查");
    } else if (req.body.indexOf("不是进行中的任务") !== -1) {
        $.notify("52破解", "", "签到失败, 原因为今日已签到或者领取任务失败");
    } else if (req.body.indexOf("任务已完成") !== -1) {
        $.notify("52破解", "", "签到成功");
    } else {
        $.notify("52破解", "", "签到失败, 签到原因未知, 请查看日志")
        console.log(req.body);
    }
}

//https://github.com/Peng-YM/QuanX/blob/master/Tools/OpenAPI/api-minified.js
function ENV(){const e="function"==typeof require&&"undefined"!=typeof $jsbox;return{isQX:"undefined"!=typeof $task,isLoon:"undefined"!=typeof $loon,isSurge:"undefined"!=typeof $httpClient&&"undefined"!=typeof $utils,isBrowser:"undefined"!=typeof document,isNode:"function"==typeof require&&!e,isJSBox:e,isRequest:"undefined"!=typeof $request,isScriptable:"undefined"!=typeof importModule}}function HTTP(e={baseURL:""}){const{isQX:t,isLoon:s,isSurge:o,isScriptable:n,isNode:i,isBrowser:r}=ENV(),u=/https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/;const a={};return["GET","POST","PUT","DELETE","HEAD","OPTIONS","PATCH"].forEach(h=>a[h.toLowerCase()]=(a=>(function(a,h){h="string"==typeof h?{url:h}:h;const d=e.baseURL;d&&!u.test(h.url||"")&&(h.url=d?d+h.url:h.url),h.body&&h.headers&&!h.headers["Content-Type"]&&(h.headers["Content-Type"]="application/x-www-form-urlencoded");const l=(h={...e,...h}).timeout,c={onRequest:()=>{},onResponse:e=>e,onTimeout:()=>{},...h.events};let f,p;if(c.onRequest(a,h),t)f=$task.fetch({method:a,...h});else if(s||o||i)f=new Promise((e,t)=>{(i?require("request"):$httpClient)[a.toLowerCase()](h,(s,o,n)=>{s?t(s):e({statusCode:o.status||o.statusCode,headers:o.headers,body:n})})});else if(n){const e=new Request(h.url);e.method=a,e.headers=h.headers,e.body=h.body,f=new Promise((t,s)=>{e.loadString().then(s=>{t({statusCode:e.response.statusCode,headers:e.response.headers,body:s})}).catch(e=>s(e))})}else r&&(f=new Promise((e,t)=>{fetch(h.url,{method:a,headers:h.headers,body:h.body}).then(e=>e.json()).then(t=>e({statusCode:t.status,headers:t.headers,body:t.data})).catch(t)}));const y=l?new Promise((e,t)=>{p=setTimeout(()=>(c.onTimeout(),t(`${a} URL: ${h.url} exceeds the timeout ${l} ms`)),l)}):null;return(y?Promise.race([y,f]).then(e=>(clearTimeout(p),e)):f).then(e=>c.onResponse(e))})(h,a))),a}function API(e="untitled",t=!1){const{isQX:s,isLoon:o,isSurge:n,isNode:i,isJSBox:r,isScriptable:u}=ENV();return new class{constructor(e,t){this.name=e,this.debug=t,this.http=HTTP(),this.env=ENV(),this.node=(()=>{if(i){return{fs:require("fs")}}return null})(),this.initCache();Promise.prototype.delay=function(e){return this.then(function(t){return((e,t)=>new Promise(function(s){setTimeout(s.bind(null,t),e)}))(e,t)})}}initCache(){if(s&&(this.cache=JSON.parse($prefs.valueForKey(this.name)||"{}")),(o||n)&&(this.cache=JSON.parse($persistentStore.read(this.name)||"{}")),i){let e="root.json";this.node.fs.existsSync(e)||this.node.fs.writeFileSync(e,JSON.stringify({}),{flag:"wx"},e=>console.log(e)),this.root={},e=`${this.name}.json`,this.node.fs.existsSync(e)?this.cache=JSON.parse(this.node.fs.readFileSync(`${this.name}.json`)):(this.node.fs.writeFileSync(e,JSON.stringify({}),{flag:"wx"},e=>console.log(e)),this.cache={})}}persistCache(){const e=JSON.stringify(this.cache,null,2);s&&$prefs.setValueForKey(e,this.name),(o||n)&&$persistentStore.write(e,this.name),i&&(this.node.fs.writeFileSync(`${this.name}.json`,e,{flag:"w"},e=>console.log(e)),this.node.fs.writeFileSync("root.json",JSON.stringify(this.root,null,2),{flag:"w"},e=>console.log(e)))}write(e,t){if(this.log(`SET ${t}`),-1!==t.indexOf("#")){if(t=t.substr(1),n||o)return $persistentStore.write(e,t);if(s)return $prefs.setValueForKey(e,t);i&&(this.root[t]=e)}else this.cache[t]=e;this.persistCache()}read(e){return this.log(`READ ${e}`),-1===e.indexOf("#")?this.cache[e]:(e=e.substr(1),n||o?$persistentStore.read(e):s?$prefs.valueForKey(e):i?this.root[e]:void 0)}delete(e){if(this.log(`DELETE ${e}`),-1!==e.indexOf("#")){if(e=e.substr(1),n||o)return $persistentStore.write(null,e);if(s)return $prefs.removeValueForKey(e);i&&delete this.root[e]}else delete this.cache[e];this.persistCache()}notify(e,t="",a="",h={}){const d=h["open-url"],l=h["media-url"];if(s&&$notify(e,t,a,h),n&&$notification.post(e,t,a+`${l?"\n多媒体:"+l:""}`,{url:d}),o){let s={};d&&(s.openUrl=d),l&&(s.mediaUrl=l),"{}"===JSON.stringify(s)?$notification.post(e,t,a):$notification.post(e,t,a,s)}if(i||u){const s=a+(d?`\n点击跳转: ${d}`:"")+(l?`\n多媒体: ${l}`:"");if(r){require("push").schedule({title:e,body:(t?t+"\n":"")+s})}else console.log(`${e}\n${t}\n${s}\n\n`)}}log(e){this.debug&&console.log(`[${this.name}] LOG: ${this.stringify(e)}`)}info(e){console.log(`[${this.name}] INFO: ${this.stringify(e)}`)}error(e){console.log(`[${this.name}] ERROR: ${this.stringify(e)}`)}wait(e){return new Promise(t=>setTimeout(t,e))}done(e={}){s||o||n?$done(e):i&&!r&&"undefined"!=typeof $context&&($context.headers=e.headers,$context.statusCode=e.statusCode,$context.body=e.body)}stringify(e){if("string"==typeof e||e instanceof String)return e;try{return JSON.stringify(e,null,2)}catch(e){return"[object Object]"}}}(e,t)}