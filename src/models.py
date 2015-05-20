# -*- coding: utf-8 -*-

import common

"""
model
This is common data model for this system
"""


class Weibo(object):
    def __init__(self, uid, mid, content,
                 extra=None, forward=None, comment=None, like=None):
        """
        构造函数，构造一个微博对象。一条微博必要的字段是uid、mid和context。
        :param uid: user id
        :param mid: micro-blog id
        :param context: 微博正文
        :param extra: 微博附带的其他东西，比如image,video,url,paper,other micro-blog,user。
        :param forward: 转发
        :param comment: 评论
        :param like: 点赞
        :return:
        """
        self.uid = uid if isinstance(uid, int) else int(uid)
        self.mid = mid if isinstance(mid, int) else int(mid)
        self.content = content if isinstance(content, str) else str(content)
        self.extra = extra
        self.forward = forward
        self.comment = comment
        self.like = like

    def __repr__(self):
        return '<Weibo %s%d/%s>' % (common.WEIBO_URL, self.uid, common.encode_mid(self.mid))

    def __cmp__(self, other):
        if isinstance(other, Weibo):
            return cmp(self.mid, other.mid)
        else:
            return cmp(self, other)


class WeiboRequest(object):
    def __init__(self, uid, mid):
        self.uid = uid if isinstance(uid, int) else int(uid)
        self.mid = mid if isinstance(mid, int) else int(mid)

    def __repr__(self):
        return '<WeiboRequest %s>' % self.get_url()

    def __cmp__(self, other):
        if isinstance(other, WeiboRequest):
            return cmp(self.mid, other.mid)
        else:
            return cmp(self, other)

    def get_url(self):
        return '%s%d/%s' % (common.WEIBO_URL, self.uid, common.encode_mid(self.mid))


if __name__ == '__main__':
    # use to test
    m1 = Weibo(1483690581, 3838129154800841, '魅魔——东方——图被微博有损压缩，收藏建议收原图——【P站：50146131 | 画师：ろんど ，有爱请给作者评分以示支持喔～源地址：')
    m2 = Weibo(1, 2, 'hehe')
    m3 = Weibo(1, '2', 123)
    print m1, m2, m3
    print m3 == m2
    r = WeiboRequest(1483690581, 3838129154800841)
    print r