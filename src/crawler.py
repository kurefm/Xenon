# -*- coding: utf-8 -*-

import base64
import json
import re
import binascii
import os
import datetime
import cPickle as pickle
from packages import rsa
from packages import requests
from packages.requests import Session
from packages.requests import compat
import common
from models import WeiboRequest
from models import Weibo
from errors import LoginError


# define
WEIBO_URL = common.WEIBO_URL
MOBILE_WEIBO_URL = common.MOBILE_WEIBO_URL
SEARCH_URL = common.SEARCH_URL
MOBILE_SEARCH_RESULT_URL = common.MOBILE_SEARCH_RESULT_URL
MOBILE_SEARCH_URL = common.MOBILE_SEARCH_URL

HTTP_TIMEOUT = common.HTTP_TIMEOUT

WEIBO_INFO_URL = 'http://weibo.com/aj/v6/{kind}/big'
WEIBO_INFO_ACCEPT_KIND = ['comment', 'forward', 'like', 'simple']

# compiled regex
RE_FIND_LOGIN_ERROR_INFO = re.compile(r'"retcode":"([^"]+?)","reason":"([^"]+?)"')
RE_FIND_MID_UID_IN_SEARCH = re.compile(r'<?div[^>]*?mid=\\"(\d+?)\\"[^>]*?>[\s\S]*?usercard=\\"[^"]*?id=(\d*)[^"]*?\\"')
RE_FIND_CONTENT_IN_WEIBO = re.compile(r'<?meta.*?content="(.*?)".*?name="description".*?/>')
RE_FIND_TIME_IN_WEIBO = re.compile(r'')


class HttpOperation(Session):
    """继承Session，添加cookie保存到文件功能，添加一些常用的http头"""

    def __init__(self, cookie_filename=None, default_headers=None):
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/42.0.2312.90 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-GB;q=0.6,en;q=0.4',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
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
        # 设定默认超时时间
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


class WeiboLogin(HttpOperation):
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
            'client': self._CLIENT,
            '_': ''
        }
        self.__login_params = {
            'entry': 'account',
            'gateway': '1',
            'from': '',
            'savestate': '30',
            'useticket': '0',
            'pagerefer': 'http%3A%2F%2Flogin.sina.com.cn%2Fsso%2Flogout.php',
            'vsnf': '1',
            'su': 'eGVub24wMDAxJTQwMTYzLmNvbQ%3D%3D',
            'service': 'sso',
            'servertime': '1431656928',
            'nonce': 'F9RO5T',
            'pwencode': 'rsa2',
            'rsakv': '1330428213',
            'sp': '63a228299e7ea8fdcbe45b39c4bd7309259d8b78d9e4a78c2d46c34526e2278243e1516351969778c868f5591a8fd472ae9ebd1976b07ffa941808b38b24867d0643bc582dbe4a92df3340267277a86d932d56e78253b863759a8952ff7246bffc4d1a24557f5432c028b05f3996225796312bf2fb71a78e6eec40427e58fb25',
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '366',
            'callback': 'parent.sinaSSOController.loginCallBack',
            'returntype': 'IFRAME',
            'setdomain': '1'
        }
        # 调用基类构造函数
        super(WeiboLogin, self).__init__(os.path.join('cookies', '[%s].cookie' % username))

        try:
            self.load_cookie()
        except IOError as ioe:
            self.relogin(username, password)
        else:
            if not self.check_login_status():
                self.relogin(username, password)

    def __prelogin(self, username, password):
        """
        predictive login, get the information to use in login
        :param username:
        :param password:
        """
        su = base64.b64encode(compat.quote(username))

        self.__prelogin_params['su'] = su
        self.__prelogin_params['_'] = common.rnd()

        html = self.get(self._PRE_LOGIN_URL, params=self.__prelogin_params,
                        headers={'Referer': self._LOGIN_ROOT_URL}).text

        json_str = re.match(r'[^{]+({.+?})', html).group(1)
        print json_str
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

        print self.__login_params

        html = self.post(self._LOGIN_URL, params=self.__login_params,
                         headers={'Referer': self._LOGIN_ROOT_URL, 'Origin': self._LOGIN_ROOT_URL})
        print html.text
        # 检查是否存在登陆错误
        error = re.search(RE_FIND_LOGIN_ERROR_INFO, html.text)
        if error:
            error_msg = common.weibo_blogs_convert(error.group(0))
            raise LoginError(error_msg)

        urls = re.findall(r'\"((http|https)[\s\S]+?)\"', html)
        for url in urls:
            self.get(url[0].replace('\\', ''))
        # 登陆完成后保存cookie
        self.save_cookie()

    def check_login_status(self):
        """
        check login
        :return: if login success return True, else return False
        """
        if self.get(WEIBO_URL).url.find(WEIBO_URL) == 0:
            return True
        else:
            return False


class MobileWeiboLogin(HttpOperation):
    _LOGIN_URL = 'https://passport.weibo.cn/sso/login'
    _HTTP_KIND = 'http'
    _DEFAULT_URL_TAIL = '&savestate=1&callback=jsonpcallback'

    _DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
    }
    _LOGIN_DATAS = {
        'username': '',
        'password': '',
        'savestate': '1',
        'ec': '0',
        'pagerefer': '',
        'entry': 'mweibo',
        'loginfrom': '',
        'client_id': '',
        'code': '',
        'hff': '',
        'hfp': '',
    }

    def __init__(self, username, password):
        cookie_filename = os.path.join('cookies', '[%s].cookie' % username)

        super(MobileWeiboLogin, self).__init__(cookie_filename, self._DEFAULT_HEADERS)

        try:
            self.load_cookie()
        except IOError as ioe:
            self.relogin(username, password)
        else:
            if not self.check_login_status():
                self.relogin(username, password)

    def __login(self, username, password):
        self._LOGIN_DATAS['username'] = username
        self._LOGIN_DATAS['password'] = password

        headers = {
            'Host': 'passport.weibo.cn',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3549&r=http%3A%2F%2Fm.weibo.cn%2F',
        }

        response = self.post(self._LOGIN_URL, data=self._LOGIN_DATAS, headers=headers)

        crossdomainlist = response.json()['data']['crossdomainlist']

        # 这一步是会设置cookie的，非常重要
        for (key, url) in crossdomainlist.items():
            url = '{0}:{1}{2}{3}'.format(self._HTTP_KIND, url, self._DEFAULT_URL_TAIL, common.rnd())
            self.get(url)

    def relogin(self, username, password):
        self.__login(username, password)
        self.save_cookie()

    def check_login_status(self):
        if self.get(MOBILE_WEIBO_URL).url.find(MOBILE_WEIBO_URL) == 0:
            return True
        else:
            return False


class WeiboCrawler(MobileWeiboLogin):
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

        print html.encode('gbk', 'ignore')

        for (mid, uid) in blog_ids:
            print mid
            # handler(WeiboRequest(uid, mid))

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


class MobileWeiboCrawler(MobileWeiboLogin):
    def get_ajax(self, url, params):
        return self.get(url, params=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def search(self, key, kind='wb', handler=None, limit=0, is_return=True):
        # kind在移动版里面可选微博（wb），所有（all），用户（user）
        # 搜索得到每页微博的html，作为参数传给handler
        kind = kind.lower()

        handler = self.search_page_handler if not handler else handler

        params = {'type': kind, 'queryVal': compat.quote(key)}

        # 请求页面
        response = self.get(MOBILE_SEARCH_RESULT_URL, params=params, headers={'Referer': MOBILE_SEARCH_URL})

        print response.url
        html = response.text
        # html=common.weibo_blogs_convert(html)
        with open('1.html', 'wb') as fp:
            fp.write(html.encode('utf-8', 'ignore'))

        blog_urls = re.findall(r'"mid":"(\d{16})"[\s\S]+?"\\/u\\/(\d+?)"', html)

        for (mid, uid) in blog_urls:
            wq = WeiboRequest(uid, mid)
            print wq.murl




        # 执行页面处理程序
        # handler(page)

        page_urls = []
        # 正则查找所有页面

        # for page_url in page_urls:
        # page = self.get(page_url, headers={'Referer': key_search_url}).text
        # # 执行页面处理程序
        # handler(page)


    def search_page_handler(self, html, handler=None, limit=0):
        # 处理html得到uid和mid（WeiboRequest），作为参数传给handler
        handler = self.get_weibo if not handler else handler

        blog_ids = re.findall(RE_FIND_MID_UID_IN_SEARCH, html)

        for (mid, uid) in blog_ids:
            handler(WeiboRequest(uid, mid))

    def get_weibo(self, weibo_request):
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
        f.readline()
        account = f.readline().split(',')
    if account:
        print account
        m = WeiboCrawler(account[0], account[1])
        print m.check_login_status()

        # print m.get(WEIBO_URL).text.encode('gbk','ignore')

        # m.search('红旗')


        # print w.search('白箱')
        # print
        # print w.check_login_state()
        # blog_requests = w.search('白箱')
        # w.get_weibo(blog_requests[0])
        # for blog_request in blog_requests:
        # w.get_weibo(blog_request)
