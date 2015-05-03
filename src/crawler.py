# -*- coding: utf-8 -*-

from common import *
import models
import urllib
import urllib2
import cookielib
import base64
import json
import re
import binascii
import os
from packages import rsa
from packages import requests
from errors import CookieTypeError


class HttpOperation(requests.Session):
    def __init__(self, cookie_filename=None, cookie_type='Mozilla', default_headers=None):
        """
        Initialize default http header and cookie
        :param cookie_filename:
        :param cookie_type:
        :param default_headers:
        """
        self._default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
            'Accept-Language': 'zh-CN'
        } if not default_headers else default_headers
        self._cookie_filename = cookie_filename
        super(HttpOperation, self).__init__()

        # 添加默认http头
        self.headers.update(self._default_headers)

        # cookie保存文件
        if cookie_filename:
            # 创建cookie，带保存文件
            if cookie_type.lower() == 'mozilla':
                self.cookies = cookielib.MozillaCookieJar(cookie_filename)
            elif cookie_type.lower() == 'lwp':
                self.cookies = cookielib.LWPCookieJar(cookie_filename)
            else:
                raise CookieTypeError("Unsupported cookie type: %s" % cookie_type)
        else:
            self.cookies = cookielib.CookieJar()

    def get(self, url, params={}, headers={}, timeout=HTTP_TIMEOUT, **kwargs):
        """
        Use get method to request page
        :param url: witch url do you want to request
        :param params: append params in request
        :param headers: append headers in request
        :param timeout:
        :return: it with return a response object
        """
        return super(HttpOperation, self).get(url, params=params, headers=headers, timeout=timeout, **kwargs)

    def post(self, url, params={}, headers={}, timeout=HTTP_TIMEOUT, **kwargs):
        """
        Use post method to request page
        :param url:witch url do you want to request
        :param params:append params in request
        :param headers:append headers in request
        :return:it with return a response object
        """
        return super(HttpOperation, self).post(url, params=params, headers=headers, timeout=timeout, **kwargs)

    def load_cookie(self, filename=None, ignore_discard=False, ignore_expires=False):
        if self._cookie_filename:
            self.cookies.load(filename, ignore_discard, ignore_expires)

    def save_cookie(self, filename=None, ignore_discard=False, ignore_expires=False):
        if self._cookie_filename:
            self.cookies.save(filename, ignore_discard, ignore_expires)


class Login(HttpOperation):
    """The class use to login weibo"""
    _CLIENT = 'ssologin.js(v1.4.15)'
    _LOGIN_ROOT_URL = 'http://login.sina.com.cn/'
    _PRE_LOGIN_URL = _LOGIN_ROOT_URL + 'sso/prelogin.php'
    _LOGIN_URL = _LOGIN_ROOT_URL + 'sso/login.php?client=' + _CLIENT
    _SEARCH_URL = 'http://s.weibo.com/'

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
            print 'cookie not exist'
            self.relogin(username, password)
        else:
            self.check_login_state()
            # if self.check_login_state():
            self.relogin(username, password)
            print 'cookie is ok'

        html=self.get(WEIBO_URL).content
        print html

    def __prelogin(self, username, password):
        """
        predictive login, get the information to use in login
        :param username:
        :param password:
        """
        su = base64.b64encode(urllib.quote(username))
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
        self.__prelogin(username, password)
        html = self.post(self._LOGIN_URL, params=self.__login_params, headers={'Referer': self._LOGIN_ROOT_URL}).text
        # print html
        urls = re.findall(r'\"((http|https)[\s\S]+?)\"', html)
        for url in urls:
            self.get(url[0].replace('\\', ''))
        # 保存cookie
        print 'login successful, save cookie'
        self.save_cookie()

    def check_login_state(self):
        """
        check login
        :return: if login success return True, else return False
        """
        # print self.get(WEIBO_URL).text.encode('gbk','ignore')
        # if self.get(WEIBO_URL).geturl().find(WEIBO_URL) == -1:
        # return False
        # elif self.get(WEIBO_URL).geturl().find(WEIBO_URL) == 0:
        # return True
        # else:
        # return False


if __name__ == '__main__':
    account = None
    with open('accounts', 'rb') as f:
        account = f.readline().split(',')
    if account:
        l = Login(account[0], account[1])