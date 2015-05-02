# -*- coding: utf-8 -*-

import urllib2


class PreLogin:
    __preLoginUrl = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)&_=1428640081522'

    def __init__(self):
        self.js = urllib2.urlopen(self.__preLoginUrl).read()


if __name__ == '__main__':
    p = PreLogin()
    print p.js