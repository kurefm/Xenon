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


class HttpOperation(Session):
    """继承Session，添加cookie保存到文件功能，添加一些常用的http头"""

    def __init__(self, cookie_filename=None, default_headers=None):
        """
        Initialize default http header and cookie
        :param cookie_filename:
        :param cookie_kind:
        :param default_headers:
        """
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
            'Accept-Language': 'zh-CN'
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

    # >>>>>>> use_requests
    #
    # html=self.get(WEIBO_URL).content
    # print html

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
        self.__login_params['sp'] = self.__encrypt_password(
            password, info['pubkey'], info['servertime'], info['nonce'])

    def __encrypt_password(self, password, publicKey, serverTime, nonce):
        key = rsa.PublicKey(int(publicKey, 16), int('10001', 16))
        message = '%s\t%s\n%s' % (str(serverTime), str(nonce), str(password))
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
    def ajax_get(self, url, params):
        return self.get(url, params=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def search(self, key, kind='weibo', handler=None, limit=0, is_return=True):
        """
        Use key to search something
        :param key: witch key do you want to search.
        :param kind: witch type do you want to search, it can be weibo,user,pic,apps in now.
        :param limit: limit search number
        :param is_return: if you use handler, cancel return to improve performance.
        :return: it with return a response object
        """
        kind = kind.lower()
        # 查询关键字编码
        key_encoded = compat.quote(compat.quote(key))
        # 拼接url
        key_search_url = '{search_url}/{kind}/{key_encoded}'.format(
            search_url=SEARCH_URL,
            kind=kind,
            key_encoded=key_encoded
        )
        # 请求页面
        page = self.get(key_search_url, headers={'Referer': SEARCH_URL})
        page = page.text
        # 解析页面
        blog_ids = re.findall(
            r'<?div[^>]*?mid=\\"(\d+?)\\"[^>]*?>[\s\S]*?usercard=\\"[^"]*?id=(\d*)[^"]*?\\"', page)

        # 返回WeiboRequest列表
        if is_return:
            blog_requests = []
            if blog_ids:
                for (mid, uid) in blog_ids:
                    request = WeiboRequest(uid, mid)
                    if handler:
                        handler(request)
                    blog_requests.append(request)
            return blog_requests
        # 不返回列表，只执行handler
        else:
            if blog_ids:
                for (mid, uid) in blog_ids:
                    if handler:
                        handler(WeiboRequest(uid, mid))

    def get_user(self, uid, handler=None):
        pass

    def get_user_weibo(self, uid, handler=None, limit=0):
        pass

    def get_weibo(self, weibo_request, handler=None, limit=0):
        url = weibo_request.get_url()

        page = self.get(url).read()
        with open(os.path.join('test', 'weibo.html'), 'wb') as f:
            f.write(page)
        print re.search(r'<?meta.*?content="(.*?)".*?name="description".*?/>', page, re.M).group(1)
        # context = re.search(r'^<?meta.*?content="(.*?)".*?name="description".*?/>$', page,re.M)
        # print context.group(1)

    def get_weibo_info(self, mid, kind='comment', handler=None, limit=0, is_return=True):
        # 检查请求类型
        if kind not in WEIBO_INFO_ACCEPT_KIND:
            raise InfoKindError('Unsupported weibo info kind: %s' % kind)

        # 检查mid
        if isinstance(mid, WeiboRequest):
            mid = mid.mid
        kind = kind.lower()

        ajax_page = None
        if kind == 'forward':
            url = WEIBO_INFO_URL.format(kind='mblog/info')
            params = {
                'ajwvr': 6,
                'mid': mid,
                'page': 1,
                '__rnd': common.rnd()
            }
            ajax_page = self.ajax_get(url, params)
        elif kind == 'simple':
            pass
        else:
            url = WEIBO_INFO_URL.format(kind=kind)
            params = {
                'ajwvr': 6,
                'id': mid,
                '__rnd': common.rnd()
            }
            ajax_page = self.ajax_get(url, params)


if __name__ == '__main__':
    account = None
    with open('accounts', 'rb') as f:
        account = f.readline().split(',')
    if account:
        w = WeiboCrawler(account[0], account[1])
        print w.search('白箱')
        # print
        print w.check_login_state()
        # blog_requests = w.search('白箱')
        # w.get_weibo(blog_requests[0])
        # for blog_request in blog_requests:
        # w.get_weibo(blog_request)
