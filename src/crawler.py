# -*- coding: utf-8 -*-

from common import *
from models import *
import urllib
import urllib2
import cookielib
import base64
import json
import re
import binascii
import os
import datetime
from packages import rsa
from errors import CookieTypeError


class HttpOperation(object):
    """Supply cookie and http method"""

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
        self._cookie = None

        # cookie保存文件
        if cookie_filename:
            self._cookie_filename = cookie_filename

            # 创建cookie，带保存文件
            if cookie_type.lower() == 'mozilla':
                self._cookie = cookielib.MozillaCookieJar(self._cookie_filename)
            elif cookie_type.lower() == 'lwp':
                self._cookie = cookielib.LWPCookieJar(self._cookie_filename)
            else:
                raise CookieTypeError("Unsupported cookie type: %s" % cookie_type)
        else:
            self._cookie = cookielib.CookieJar()


        # 用cookiejar创建build_opener
        _opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookie))
        # 将opener装入urllib2
        urllib2.install_opener(_opener)


    def __get_response(self, url, params={}, headers={}, timeout=HTTP_TIMEOUT):
        data = None

        # 对参数编码
        if params:
            data = urllib.urlencode(params)
        # 创建Request对象
        request = urllib2.Request(url, data, headers)
        # 添加默认Header
        for (key, value) in self._default_headers.items():
            if key not in request.headers:
                request.headers[key] = value
        # 打开url连接
        return urllib2.urlopen(request, timeout=timeout)

    def get(self, url, params={}, headers={}, timeout=HTTP_TIMEOUT):
        """
        Use get method to request page
        :param url:witch url do you want to request
        :param params:append params in request
        :param headers:append headers in request
        :return:it with return a response object
        """
        if params:
            url = '{url}?{encoded_params}'. \
                format(url=url, encoded_params=urllib.urlencode(params))
        return self.__get_response(url, headers=headers, timeout=timeout)

    def post(self, url, params={}, headers={}, timeout=HTTP_TIMEOUT):
        """
        Use post method to request page
        :param url:witch url do you want to request
        :param params:append params in request
        :param headers:append headers in request
        :return:it with return a response object
        """
        return self.__get_response(url, params, headers, timeout=timeout)

    def load_cookie(self, filename=None, ignore_discard=False, ignore_expires=False):
        if self._cookie_filename:
            self._cookie.load(filename, ignore_discard, ignore_expires)

    def save_cookie(self, filename=None, ignore_discard=False, ignore_expires=False):
        if self._cookie_filename:
            self._cookie.save(filename, ignore_discard, ignore_expires)


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

        super(Login, self).__init__(os.path.join('cookies', '[%s].cookie' % username))

        try:
            self.load_cookie()
        except IOError as ioe:
            self.relogin(username, password)
        else:
            if not self.check_login_state():
                self.relogin(username, password)


    def __prelogin(self, username, password):
        """
        predictive login, get the information to use in login
        :param username:
        :param password:
        """
        su = base64.b64encode(urllib.quote(username))
        self.__prelogin_params['su'] = su
        html = self.get(self._PRE_LOGIN_URL, self.__prelogin_params, {'Referer': self._LOGIN_ROOT_URL}).read()
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
        html = self.post(self._LOGIN_URL, self.__login_params, {'Referer': self._LOGIN_ROOT_URL}).read()
        urls = re.findall(r'\"((http|https)[\s\S]+?)\"', html)
        for url in urls:
            self.get(url[0].replace('\\', ''))
        # 保存cookie
        self.save_cookie()

    def check_login_state(self):
        """
        check login
        :return: if login success return True, else return False
        """
        if self.get(WEIBO_URL).geturl().find(WEIBO_URL) == -1:
            return False
        elif self.get(WEIBO_URL).geturl().find(WEIBO_URL) == 0:
            return True
        else:
            return False


class WeiboCrawler(Login):
    def search(self, key, type='weibo', handler=None, limit=0):
        """
        Use key to search something
        :param key:witch key do you want to search.
        :param type:witch type do you want to search, it can be weibo,user,pic,apps in now.
        :return:it with return a response object
        """
        type = type.lower()
        key_encoded = urllib.quote(urllib.quote(key))
        key_search_url = '{search_url}/{type}/{key_encoded}'.format(
            search_url=SEARCH_URL,
            type=type,
            key_encoded=key_encoded
        )
        page = self.get(key_search_url, headers={'Referer': SEARCH_URL}).read()
        # print 'analysis'
        blog_ids = re.findall(r'<?div[^>]*?mid=\\"(\d+?)\\"[^>]*?>[\s\S]*?usercard=\\"[^"]*?id=(\d*)[^"]*?\\"', page)
        blog_requests = []
        if blog_ids:
            for (mid, uid) in blog_ids:
                blog_requests.append(WeiboRequest(uid, mid))
        return blog_requests

    def get_user(self, uid, handler=None):
        pass

    def get_user_weibo(self, uid, handler=None, limit=0):
        pass

    def get_weibo(self, weibo_request, handler=None, limit=0):
        url = weibo_request.get_url()
        page = self.get(url).read()
        print re.search(r'<?meta.*?content="(.*?)".*?name="description".*?/>', page, re.M).group(1)
        # context = re.search(r'^<?meta.*?content="(.*?)".*?name="description".*?/>$', page,re.M)
        # print context.group(1)


if __name__ == '__main__':
    account = None
    with open('accounts', 'rb') as f:
        account = f.readline().split(',')
    if account:
        w = WeiboCrawler(account[0], account[1])
        blog_requests = w.search('白箱')
        for blog_request in blog_requests:
            w.get_weibo(blog_request)
