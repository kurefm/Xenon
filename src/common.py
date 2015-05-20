# -*- coding: utf-8 -*-

import base62
import time
import re

# Define something common constants
WEIBO_URL = 'http://weibo.com/'
SEARCH_URL = 'http://s.weibo.com/'
HTTP_TIMEOUT = 5

MID_MAX_LENGTH = 16
MID_MIN_LENGTH = 16


# Control char convert table
CTRL_CHAR_TABLE = {
    r'\n': '\n',
    r'\t': '\t'
}


def check_mid(mid):
    if len(mid) > MID_MAX_LENGTH:
        return False
    elif len(mid) < MID_MIN_LENGTH:
        return False
    else:
        return True



def decode_mid(url):
    url = str(url)[::-1]
    size = len(url) / 4 if len(url) % 4 == 0 else len(url) / 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(base62.decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))


def encode_mid(midint):
    midint = str(midint)[::-1]
    size = len(midint) / 7 if len(midint) % 7 == 0 else len(midint) / 7 + 1
    result = []
    for i in range(size):
        s = midint[i * 7: (i + 1) * 7][::-1]
        s = base62.encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4:
            s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)


def rnd():
    return int(time.time() * 1000)


def unicode_hex_to_str(unicode_hex):
    unicode_str = unicode_hex.group()
    if len(unicode_str) == 2:
        # len=2 is a char
        try:
            return CTRL_CHAR_TABLE[unicode_str]
        except KeyError:
            return unicode_str[1:]
    if len(unicode_str) == 6:
        # len=6 is a unicode char
        return unicode_hex.group().decode('unicode_escape')


def weibo_blogs_convert(weibo_blogs):
    return re.sub(r'\\((u[0-9A-Fa-f]{4})|\S)', unicode_hex_to_str, weibo_blogs)
