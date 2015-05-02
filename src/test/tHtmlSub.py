# -*- coding: utf-8 -*-

import re
import json
import codecs

# Control char convert table
CTRL_CHAR_TABLE = {
    r'\n': '\n',
    r'\t': '\t'
}


def unicode_hex_to_str(unicode_hex):
    unicode_str = unicode_hex.group()
    if len(unicode_str) == 2:
        # len=2 is a char
        try:
            return CTRL_CHAR_TABLE[unicode_str]
        except KeyError as ke:
            return unicode_str[1:]
    if len(unicode_str) == 6:
        # len=6 is a unicode char
        return unicode_hex.group().decode('unicode_escape')


def weibo_blogs_convert(weibo_blogs):
    return re.sub(r'\\((u[0-9A-Fa-f]{4})|\S)', unicode_hex_to_str, weibo_blogs)


def get_weibo_direct_html(html):
    # if can't find pl_weibo_direct, it don't return anything
    result = re.search(r'\{"pid":"pl_weibo_direct"[\s\S]+?\}', html)
    if result:
        weibo_direct_json = json.loads(result.group())
        return weibo_direct_json['html']


def remove_key_highlight(html):
    return re.sub(r'<em class="red">([\s\S]*?)</em>', r'\1', html)


def get_blogs(html):
    pass


if __name__ == '__main__':
    # to test the function
    input_filename = 'log.html'
    output_filename = 'format.html'
    buffer = ""
    with open(input_filename, 'r') as f:
        buffer = f.read()

    result = get_weibo_direct_html(buffer)
    print type(result)
    # print result

    result = remove_key_highlight(result)
    # print result
    print type(result)

    result = weibo_blogs_convert(result)
    # print result
    print type(result)

    get_blogs(result)

    with codecs.open(output_filename, 'w',"utf-8") as f:
        f.write(result)


