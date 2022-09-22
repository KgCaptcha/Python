from wsgiref.simple_server import make_server
from sdk.KgCaptchaSDK import KgCaptcha


def start(environ, response):
    # 填写你的 AppId，在应用管理中获取
    AppID = "rA9qRcl6"
    # 填写你的 AppSecret，在应用管理中获取
    AppSecret = "6h75TuboCunnHNQhI5zzxZOZav0Wzf9e"

    request = KgCaptcha(AppID, AppSecret)

    # 填写应用服务域名，在应用管理中获取
    request.appCdn = "https://cdn9.kgcaptcha.com"

    # 请求超时时间，秒
    request.connectTimeout = 10

    # 用户id/登录名/手机号等信息，当安全策略中的防控等级为3时必须填写
    request.userId = "kgCaptchaDemo"

    # 使用其它 WEB 框架时请删除 request.parse，使用框架提供的方法获取以下相关参数
    parseEnviron = request.parse(environ)

    # 有数据提交，后端逻辑处理
    if parseEnviron["post"]:
        # 前端验证成功后颁发的 token，有效期为两分钟
        request.token = parseEnviron["post"].get("kgCaptchaToken", "")  # 前端 _POST["kgCaptchaToken"]
        # 客户端IP地址
        request.clientIp = parseEnviron["ip"]
        # 客户端浏览器信息
        request.clientBrowser = parseEnviron["browser"]
        # 来路域名
        request.domain = parseEnviron["domain"]

        # 发送请求
        requestResult = request.sendRequest()
        if requestResult.code == 0:
            # 验证通过逻辑处理
            #
            # 这里做验证通过后的数据处理
            # 如登录 / 注册场景，这里通常查询数据库、校验密码、进行登录或注册等动作处理
            # 如短信场景，这里可以开始向用户发送短信等动作处理
            # ...
            html = "<script>alert('验证通过');history.back();</script>"
        else:
            # 验证失败逻辑处理
            html = f"<script>alert('{requestResult.msg} - {requestResult.code}');history.back();</script>"
    # 无数据，显示前端表单/模板
    else:
        fp = open("./tpl/frontend.html", "rb")
        html = str(fp.read().decode(encoding="utf-8", errors="strict"))
        fp.close()

    response("200 OK", [("Content-type", "text/html; charset=utf-8")])
    return [bytes(str(html), encoding="utf-8")]


# 设置调试端口  http://localhost:8088/
httpd = make_server("0.0.0.0", 8088, start)
httpd.serve_forever()
