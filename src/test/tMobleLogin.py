# -*- coding: utf-8 -*-


import requests
import urllib2
import urllib

headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-GB;q=0.6,en;q=0.4',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.3; Nexus 7 Build/JSS15Q) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2307.2 Mobile Safari/537.36',
    'DNT': '1',
    'Host': 'login.sina.com.cn',
}

data = {
    'username': 'h6hummer@live.cn',
    'password': 'cpu-123456',
    'savestate': '1',
    'ec': '0',
    'pagerefer': 'http//passport.sina.cn/sso/logout?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn',
    'entry': 'mweibo',
    'loginfrom': '',
    'client_id': '',
    'code': '',
    'hff': '',
    'hfp': ''
}

# s = requests.Session()
# s.headers.update(headers)
# html = s.get(
# 'https://login.sina.com.cn/sso/prelogin.php?checkpin=1&entry=mweibo&su=aDZodW1tZXIlNDBsaXZlLmNu&callback=jsonpcallback1431660773858',
# timeout=15)
# # print html.text
# html = s.post('https://passport.weibo.cn/sso/login', data=data,
# headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=15)
#
# print html.text
# print s.get('http://m.weibo.cn/').text

import httplib

conn = httplib.HTTPConnection('passport.weibo.cn')

headers = {
    'Host': 'passport.weibo.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3549&r=http%3A%2F%2Fm.weibo.cn%2F',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

body = "username=h6hummer%40live.cn&password=cpu-123456&savestate=1&ec=0&pagerefer=http%3A%2F%2Fpassport.sina.cn%2Fsso%2Flogout%3Fentry%3Dmweibo%26r%3Dhttp%253A%252F%252Fm.weibo.cn&entry=mweibo&loginfrom=&client_id=&code=&hff=&hfp="

# conn.request('POST', '/sso/login', body, headers)
#
# content = conn.getresponse().read()
# print len(content)
#
# # print content
#
# import StringIO
# import gzip
#
# compressedstream = StringIO.StringIO(content)
# gzipper = gzip.GzipFile(fileobj=compressedstream)
# data = gzipper.read()
# print data

s=requests.Session()
s.headers.update(headers)

print urllib.urlencode(data)


r = s.post('https://passport.weibo.cn/sso/login', data=data)
print r.content