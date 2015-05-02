# -*- coding: utf-8 -*-

import common

"""
model
This is common data model for this system
"""


class MicroBlog(object):
    def __init__(self, uid, mid, context,
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
        self.context = context if isinstance(context, str) else str(context)
        self.extra = extra
        self.forward = forward
        self.comment = comment
        self.like = like

    def __repr__(self):
        return '<MicroBlog %s%d/%s>' % (common.WEIBO_URL, self.uid, common.encode_mid(self.mid))

    def __cmp__(self, other):
        if isinstance(other, MicroBlog):
            return cmp(self.mid, other.mid)
        else:
            return cmp(self, other)


if __name__ == '__main__':
    # use to test
    m1 = MicroBlog(1483690581, 3838129154800841, '魅魔——东方——图被微博有损压缩，收藏建议收原图——【P站：50146131 | 画师：ろんど ，有爱请给作者评分以示支持喔～源地址：')
    m2 = MicroBlog(1, 2, 'hehe')
    m3 = MicroBlog(1, '2', 123)
    print m1, m2, m3
    print m3 == m2