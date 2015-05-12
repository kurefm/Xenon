# -*- coding: utf-8 -*-

import base64
import json
import re
import binascii
import os
import datetime
import pickle
from packages import rsa
from packages import requests
from packages.requests import Session
from packages.requests import compat
import common
from models import WeiboRequest
from models import Weibo
from errors import CookieKindError
from errors import InfoKindError

WEIBO_URL = common.WEIBO_URL
SEARCH_URL = common.SEARCH_URL
HTTP_TIMEOUT = common.HTTP_TIMEOUT

WEIBO_INFO_URL = 'http://weibo.com/aj/v6/{kind}/big'
WEIBO_INFO_ACCEPT_KIND = ['comment', 'forward', 'like', 'simple']

# compiled regex
RE_FIND_MID_UID_IN_SEARCH = re.compile(r'<?div[^>]*?mid=\\"(\d+?)\\"[^>]*?>[\s\S]*?usercard=\\"[^"]*?id=(\d*)[^"]*?\\"')
RE_FIND_CONTENT_IN_WEIBO = re.compile(r'<?meta.*?content="(.*?)".*?name="description".*?/>')
RE_FIND_TIME_IN_WEIBO = re.compile(r'')


class HttpOperation(Session):
    """继承Session，添加cookie保存到文件功能，添加一些常用的http头"""

    def __init__(self, cookie_filename=None, default_headers=None):
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
            'Accept-Language': 'zh-CN',
            'Accept-Encoding': 'gzip, deflate'
        } if not default_headers else default_headers

        self.cookie_filename = cookie_filename

        super(HttpOperation, self).__init__()

        # 添加默认http头
        self.headers.update(self.default_headers)

    def get(self, url, timeout=HTTP_TIMEOUT, **kwargs):
        """
        Use get method to request page
        :param url: witch url do you want to request
        :param params: append params in request
        :param headers: append headers in request
        :param timeout:
        :return: it with return a response object
        """
        kwargs['timeout'] = timeout
        return super(HttpOperation, self).get(url, **kwargs)

    def post(self, url, timeout=HTTP_TIMEOUT, **kwargs):
        """
        Use post method to request page
        :param url:witch url do you want to request
        :param params:append params in request
        :param headers:append headers in request
        :return:it with return a response object
        """
        kwargs['timeout'] = timeout
        return super(HttpOperation, self).post(url, **kwargs)

    # 序列化RequestsCookieJar来保存cookie
    def load_cookie(self, filename=None):
        cookie_filename = self.cookie_filename if not filename else filename
        with open(cookie_filename, 'rb') as cookie_file:
            self.cookies = pickle.load(cookie_file)

    # 读取序列化的RequestsCookieJar对象
    def save_cookie(self, filename=None):
        cookie_filename = self.cookie_filename if not filename else filename
        with open(cookie_filename, 'wb') as cookie_file:
            pickle.dump(self.cookies, cookie_file)


class Login(HttpOperation):
    """The class use to login weibo"""
    _CLIENT = 'ssologin.js(v1.4.15)'
    _LOGIN_ROOT_URL = 'http://login.sina.com.cn/'
    _PRE_LOGIN_URL = _LOGIN_ROOT_URL + 'sso/prelogin.php'
    _LOGIN_URL = _LOGIN_ROOT_URL + 'sso/login.php?client=' + _CLIENT

    def __init__(self, username, password):
        self.__prelogin_params = {
            'entry': 'account',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': '',
            'rsakt': 'mod',
            'client': self._CLIENT
        }
        self.__login_params = {
            'entry': 'account',
            'gateway': '1',
            'from': '',
            'savestate': '30',
            'useticket': '0',
            'pagerefer': '',
            'vsnf': '1',
            'su': '',
            'service': 'sso',
            'servertime': '1429884778',
            'nonce': 'GAFUK7',
            'pwencode': 'rsa2',
            'rsakv': '1330428213',
            'sp': '',
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '34925',
            'callback': 'parent.sinaSSOController.loginCallBack',
            'returntype': 'IFRAME',
            'setdomain': '1'
        }
        # 调用基类构造函数
        super(Login, self).__init__(os.path.join('cookies', '[%s].cookie' % username))

        try:
            self.load_cookie()
        except IOError as ioe:
            self.relogin(username, password)
        else:
            if not self.check_login_state():
                self.relogin(username, password)

    def __del__(self):
        self.save_cookie()

    def __prelogin(self, username, password):
        """
        predictive login, get the information to use in login
        :param username:
        :param password:
        """
        su = base64.b64encode(compat.quote(username))
        self.__prelogin_params['su'] = su
        html = self.get(self._PRE_LOGIN_URL, params=self.__prelogin_params,
                        headers={'Referer': self._LOGIN_ROOT_URL}).text

        json_str = re.match(r'[^{]+({.+?})', html).group(1)
        info = json.loads(json_str)

        self.__login_params['su'] = su
        self.__login_params['servertime'] = info['servertime']
        self.__login_params['nonce'] = info['nonce']
        self.__login_params['rsakv'] = info['rsakv']
        self.__login_params['sp'] = self.__encrypt_password(password, info['pubkey'], info['servertime'], info['nonce'])

    @staticmethod
    def __encrypt_password(password, public_key, server_time, nonce):
        key = rsa.PublicKey(int(public_key, 16), int('10001', 16))
        message = '%s\t%s\n%s' % (str(server_time), str(nonce), str(password))
        password = rsa.encrypt(message.encode('utf-8'), key)
        return binascii.b2a_hex(password)

    def relogin(self, username, password):
        """
        if login failed, you can use this method to login again
        :param username: username
        :param password: password
        """
        # 执行完整的登陆过程
        self.__prelogin(username, password)

        html = self.post(self._LOGIN_URL, params=self.__login_params, headers={'Referer': self._LOGIN_ROOT_URL}).text

        urls = re.findall(r'\"((http|https)[\s\S]+?)\"', html)
        for url in urls:
            self.get(url[0].replace('\\', ''))
        self.save_cookie()

    def check_login_state(self):
        """
        check login
        :return: if login success return True, else return False
        """
        if self.get(WEIBO_URL).url.find(WEIBO_URL) == 0:
            return True
        else:
            return False


class WeiboCrawler(Login):
    def get_ajax(self, url, params):
        return self.get(url, params=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def search(self, key, kind='weibo', handler=None, limit=0, is_return=True):
        # 搜索得到每页微博的html，作为参数传给handler
        kind = kind.lower()
        # 查询关键字编码
        key_encoded = compat.quote(compat.quote(key))
        # 拼接url
        key_search_url = '{search_url}/{kind}/{key_encoded}'.format(
            search_url=SEARCH_URL,
            kind=kind,
            key_encoded=key_encoded
        )

        handler = self.search_page_handler if not handler else handler

        # 请求页面
        page = self.get(key_search_url, headers={'Referer': SEARCH_URL}).text

        # 执行页面处理程序
        handler(page)

        page_urls = []
        # 正则查找所有页面

        for page_url in page_urls:
            page = self.get(page_url, headers={'Referer': key_search_url}).text
            # 执行页面处理程序
            handler(page)


    def search_page_handler(self, html, handler=None, limit=0):
        # 处理html得到uid和mid（WeiboRequest），作为参数传给handler
        handler = self.weibo_handler if not handler else handler

        blog_ids = re.findall(RE_FIND_MID_UID_IN_SEARCH, html)

        for (mid, uid) in blog_ids:
            handler(WeiboRequest(uid, mid))

    def weibo_handler(self, weibo_request):
        # 请求微博页面，遍历转发，评论，点赞信息。
        html = self.get(weibo_request.url)

        uid = weibo_request.uid
        mid = weibo_request.mid
        content = re.search(RE_FIND_CONTENT_IN_WEIBO, html, re.M).group(1)
        time = re.search(RE_FIND_TIME_IN_WEIBO, html)

        weibo = Weibo(uid, mid, content, time)

        weibo.forward = self.travels_forward(mid)
        weibo.comment = self.travels_comment(mid)
        weibo.like = self.travels_like(mid)

        return weibo

    def travels_forward(self, mid, handler=None):
        # 遍历转发，返回WeiboRequest列表
        # 使用ajax请求数据，每部分数据交由handler处理

        params = {
            'ajwvr': 6,
            'id': mid,
            '__rnd': common.rnd()
        }

        forwards = []

        url = WEIBO_INFO_URL.format(kind='forward')
        # 请求第一页数据
        ajax_data = self.get_ajax(url, params=params)
        forwards.extend(handler(ajax_data))

        # 获取页数
        page_num = 0

        # 遍历页数
        for num in range(2, page_num + 1):
            params['page'] = num
            ajax_data = self.get_ajax(url, params=params)
            forwards.extend(handler(ajax_data))

        return forwards

    def travels_comment(self, mid, handler=None):
        # 遍历评论，返回WeiboComment列表
        # 使用ajax请求数据，每部分数据交由handler处理

        params = {
            'ajwvr': 6,
            'id': mid,
            '__rnd': common.rnd()
        }

        comments = []

        url = WEIBO_INFO_URL.format(kind='comment')
        # 请求第一页数据
        ajax_data = self.get_ajax(url, params=params)
        comments.extend(handler(ajax_data))

        # 获取页数
        page_num = 0

        # 遍历页数
        for num in range(2, page_num + 1):
            params['page'] = num
            ajax_data = self.get_ajax(url, params=params)
            comments.extend(handler(ajax_data))

        return comments

    def travels_like(self, mid, handler=None):
        # 遍历评论，返回uid列表
        # 使用ajax请求数据，每部分数据交由handler处理

        params = {
            'ajwvr': 6,
            'id': mid,
            '__rnd': common.rnd()
        }

        likes = []

        url = WEIBO_INFO_URL.format(kind='forward')
        # 请求第一页数据
        ajax_data = self.get_ajax(url, params=params)
        likes.extend(handler(ajax_data))

        # 获取页数
        page_num = 0

        # 遍历页数
        for num in range(2, page_num + 1):
            params['page'] = num
            ajax_data = self.get_ajax(url, params=params)
            likes.extend(handler(ajax_data))

        return likes

    def forward_ajax_handler(self, json_str):
        # 处理每页ajax数据，得到WeiboRequest列表
        pass

    def comment_ajax_handler(self, json_str):
        # 处理每页ajax数据，得到WeiboComment列表
        pass

    def like_ajax_handler(self, json_str):
        # 处理每页ajax数据，得到uid列表
        pass


if __name__ == '__main__':
    account = None
    with open('accounts', 'rb') as f:
        account = f.readline().split(',')
    if account:
        w = WeiboCrawler(account[0], account[1])
        # print w.search('白箱')
        # print
        print w.check_login_state()
        # blog_requests = w.search('白箱')
        # w.get_weibo(blog_requests[0])
        # for blog_request in blog_requests:
        # w.get_weibo(blog_request)
