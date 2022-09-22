# -*- coding:utf-8 -*-
# Python 3.10
# KgCaptcha v1.0.0
# http://www.KgCaptcha.com
#
# Copyright © 2022 Kyger. All Rights Reserved.
# http://www.kyger.com.cn
#
# Copyright © 2022 by KGCMS.
# http://www.kgcms.com
#
# Date: Thu May 20 15:28:23 2022
#

from time import time
from json import loads
from hashlib import md5
from collections import namedtuple
from urllib.request import urlopen, Request
from urllib.parse import parse_qs, urlencode


class KgCaptcha(object):
    """
    Python SDK，Python 3.10
    """
    appCdn = "https://cdn.kgcaptcha.com"  # 风险防控服务URL

    # 公钥/秘钥
    appId = appSecret = None

    connectTimeout = 50  # 连接超时断开请求，秒

    # 客户端信息：IP/浏览器/用户ID
    clientIp = clientBrowser = userId = None

    domain = ""  # 授权域名，当前应用域名
    token = ""  # 前端验证成功后颁发的 token

    time = int(time())  # 当前时间
    data = {}  # 请求数据

    def __init__(self, appid, secret):
        self.appId = appid  # 公钥
        self.appSecret = secret  # 秘钥

    # 数据包
    def putData(self):
        return {
            "ip": self.clientIp,
            "browser": self.clientBrowser,
            "time": self.time,
            "uid": self.userId,
            "timeout": self.connectTimeout,
            "token": self.token,
        }

    # 生成签名URL
    def signUrl(self):
        rData = ""
        self.data = self.putData()
        for key, value in self.data.items():
            rData += str(key) + str(value)
        sign = md5(str(self.appId + rData + self.appSecret).encode(encoding="UTF-8")).hexdigest()
        return f"{self.appCdn}/requestBack?appid={self.appId}&sign={sign}"

    def sendRequest(self):
        url = self.signUrl()
        data = urlencode(self.data).encode("utf-8")
        r = urlopen(
            url=Request(
                url=url,
                data=data,
                headers={
                    "REFERER": self.domain,
                },
                method="POST"
            ), timeout=self.connectTimeout).read()
        if isinstance(r, bytes): r = r.decode("utf-8")
        r = loads(r)
        return namedtuple("ObjectName", r.keys())(*r.values())

    def parse(self, environ):
        """
        WSGI environ环境变量解析，使用其它框架获取 GET/POST 参数时可以忽略
        """
        # 解析 WSGI environ 变量中的 POST 参数
        post = get = {}
        length = str(environ.get('CONTENT_LENGTH', 0))
        if length.isnumeric():
            form_data = environ['wsgi.input'].read(int(length))
            if form_data:
                post = parse_qs(form_data.decode(encoding="utf-8"), True)
        for k, v in post.items(): post[k] = v[0]

        get = parse_qs(environ.get('QUERY_STRING', ""), True)
        for k, v in get.items(): get[k] = v[0]

        return {
            "ip": environ.get('HTTP_X_FORWARDED_FOR', environ.get('REMOTE_ADDR', '')),  # IP地址
            "get": get,  # GET
            "post": post,  # POST
            "browser": environ.get('HTTP_USER_AGENT', ""),  # 浏览器
            "domain": environ.get('HTTP_REFERER', ""),  # 来源域名
        }
