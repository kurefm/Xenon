# -*- coding: utf-8 -*-

import sys

sys.path.append('../3rd/')
sys.path.append('../')

import requests

import urllib
import urllib2
import cookielib
import base64
import json
import re
import rsa
import binascii


class Login(object):
    _CLIENT = 'ssologin.js(v1.4.15)'
    _LOGIN_ROOT_URL = 'http://login.sina.com.cn/'
    _PRE_LOGIN_URL = _LOGIN_ROOT_URL + 'sso/prelogin.php'
    _LOGIN_URL = _LOGIN_ROOT_URL + 'sso/login.php?client=' + _CLIENT
    _SEARCH_URL = 'http://s.weibo.com/'
    _WEIBO_URL = 'http://weibo.com/'
    __USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    __LANGUAGE = 'zh-CN'

    __prelogin_params = {
        'entry': 'account',
        'callback': 'sinaSSOController.preloginCallBack',
        'su': '',
        'rsakt': 'mod',
        'client': _CLIENT
    }
    __login_params = {
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

    def __init__(self, username, password):
        # 创建cookie
        cookie = cookielib.CookieJar()
        # 用cookiejar创建build_opener
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        # 将opener装入urllib2
        urllib2.install_opener(opener)
        self.__login(username, password)
        # with open('log.html', 'w') as f:
        # f.write(self.get('http://s.weibo.com/weibo/%25E7%2599%25BD%25E7%25AE%25B1',
        # {'Referer': 'http://s.weibo.com/'}).read())
        print self.get(self._WEIBO_URL).geturl().find(self._WEIBO_URL)

    def __get_response(self, url, params={}, headers={}):
        data = None

        # 对参数编码
        if params:
            data = urllib.urlencode(params)

        # 创建Request对象
        request = urllib2.Request(url, data, headers)
        # 添加默认Header
        request.add_header('User-Agent', self.__USER_AGENT)
        request.add_header('Accept-Language', self.__LANGUAGE)
        # 打开url连接
        return urllib2.urlopen(request)

    def __prelogin(self, username, password):
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

    def __login(self, username, password):
        self.__prelogin(username, password)
        html = self.post(self._LOGIN_URL, self.__login_params, {'Referer': self._LOGIN_ROOT_URL}).read()
        # print html.decode('unicode_escape').encode('gb2312','replace').replace('\\', '')
        urls = re.findall(r'\"((http|https)[\s\S]+?)\"', html)
        for url in urls:
            self.get(url[0].replace('\\', ''))

    def __check_login_state(self):
        if self.get(self._WEIBO_URL).geturl().find(self._WEIBO_URL) == -1:
            return False
        elif self.get(self._WEIBO_URL).geturl().find(self._WEIBO_URL) == 0:
            return True
        else:
            return False

    def get(self, url, params={}, headers={}):
        """
        Use get method to request page
        :param url:witch url do you want to request
        :param params:append params in request
        :param headers:append headers in request
        :return:it with return a response object
        """
        if params:
            url = '{url}?{encoded_params}'.format(url=url,
                                                  encoded_params=urllib.urlencode(params))
        return self.__get_response(url, headers=headers)

    def post(self, url, params={}, headers={}):
        """
        Use post method to request page
        :param url:witch url do you want to request
        :param params:append params in request
        :param headers:append headers in request
        :return:it with return a response object
        """
        return self.__get_response(url, params, headers)

    def search(self, key, type='weibo'):
        """
        Use key to search something
        :param key:witch key do you want to search.
        :param type:witch type do you want to search, it can be weibo,user,pic,apps in now.
        :return:it with return a response object
        """
        key_encoded = urllib.quote(urllib.quote(key))
        key_search_url = '{search_url}/{type}/{key_encoded}'.format(
            search_url=self._SEARCH_URL,
            type=type,
            key_encoded=key_encoded
        )
        return self.get(key_search_url, headers={'Referer': self._SEARCH_URL})


if __name__ == '__main__':
    l = Login('h6hummer@live.cn', 'sina281206')

