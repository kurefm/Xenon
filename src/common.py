# -*- coding: utf-8 -*-

import random
import base62
import time
import re

# Define something common constants
WEIBO_URL = 'http://weibo.com/'
MOBILE_WEIBO_URL = 'http://m.weibo.cn/'
SEARCH_URL = 'http://s.weibo.com/'
MOBILE_SEARCH_RESULT_URL = 'http://m.weibo.cn/searchs/result'
MOBILE_SEARCH_URL = 'http://m.weibo.cn/searchs'
HTTP_TIMEOUT = 15

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
    return int(time.time() * 1000 + random.random() * 10000)


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


class Section(object):
    def __init__(self, config_obj, section):
        if section not in config_obj.sections():
            from errors import NoSectionError

            raise NoSectionError('No section: %s' % section)
        super(Section, self).__init__()
        self.__dict__['config'] = config_obj
        self.__dict__['section'] = section

    def __getattr__(self, option):
        return self.config.get(self.section, option)

    def __setattr__(self, option, value):
        self.config.set(self.section, option, value)

    def __iter__(self):
        return self.config.options(self.section).__iter__()


from ConfigParser import ConfigParser


class Configuration(ConfigParser):
    def __init__(self, filename):
        ConfigParser.__init__(self)
        self.filename = filename
        self.read(filename)

    def __getattr__(self, section):
        return Section(self, section)

    def __iter__(self):
        return self.sections().__iter__()

    def __str__(self):
        return '<Configuration Object>'

    def __repr__(self):
        self.__str__(self)

    def __dir__(self):
        return dir(ConfigParser) + ['filename', 'save', 'reload']

    def reload(self, filename=None):
        self.read(filename)

    def save(self, filename=None):
        filename = self.filename if not filename else filename

        with open(filename, 'wb') as fp:
            self.write(fp)

# 全局配置
CONFIG = Configuration('config')


def weibo_blogs_convert(weibo_blogs):
    return re.sub(r'\\((u[0-9A-Fa-f]{4})|\S)', unicode_hex_to_str, weibo_blogs)


if __name__ == '__main__':
    config = CONFIG
    print config.app.name
    config.app.editor = 'kure'
    # config.add_section('language')
    config.language.cn = '氙'
    config.save()
