# -*- coding: utf-8 -*-

WF = 1
WM = 1
WC = 1
WL = 1


class DB(object):
    def __init__(self):
        # data
        self.uid = [0, 1, 2, 3, 4]
        self.mid = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.cid = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        self.user_rank = [10.0, 10.0, 10.0, 10.0, 10.0]

        self.mblog_rank = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        self.comment_rank = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        # relation
        self.follower = [
            [2, 3, 4],
            [0],
            [2, 4],
            [0, 1, 4],
            [0, 1, 2, 3]
        ]

        self.user_mblog = [
            [0],
            [1, 2, 3, 4],
            [],
            [5, 6, 7],
            [8, 9]
        ]

        self.user_comment = [
            [0],
            [1, 2, 3, 4],
            [],
            [5, 6, 7],
            [8, 9]
        ]

        self.forword=[
            []
        ]

        self.mblog_comment = [
            [0],
            [1, 2],
            [],
            [],
            [3, 4, 5],
            [6],
            [7],
            [8, 9],
            [],
            []
        ]

        self.mblog_like = [
            [2, 3],
            [0, 1],
            [1, 2, 3, 4],
            [],
            [],
            [],
            [0, 1, 2, 3, 4],
            [2, 3, 4],
            [0, 4],
            [2, 4]
        ]

        self.comment_like = [
            [0, 2, 3],
            [0, 1],
            [1, 2, 3, 4],
            [1, 2],
            [2, 4],
            [],
            [0, 1, 2, 3, 4],
            [2, 3, 4],
            [0, 4],
            [2, 4]
        ]

    def user_follow_num(self, uidA):
        following = []
        for uidB, followers in enumerate(self.follower):
            if uidA in followers:
                following.append(uidB)
        return len(following)

    def user_mblog_num(self, uid):
        return len(self.user_mblog)

    def user_comment_num(self, uid):
        return len(self.user_comment)

    def user_like_num(self, uid):
        counter = 0
        for likes in self.mblog_like:
            if uid in likes:
                counter += 1
        for likes in self.comment_like:
            if uid in likes:
                counter += 1
        return counter

    def who_s_mblog(self,mid):
        for uid,mids in enumerate(self.user_mblog):
            if mid in mids:
                return uid


db = DB()


def br(uid):
    s = db.user_follow_num(uid) * WF + \
        db.user_mblog_num(uid) * WM + \
        db.user_comment_num(uid) * WC + \
        db.user_like_num(uid) * WL
    return db.user_rank[uid] / s
    pass


def ur(uid):
    rank = 0
    for user in db.follower[uid]:
        rank += br(user) * WF
    return rank
    pass


def mbr(mid):
    rank=br(db.who_s_mblog(mid))*WM
    for forward in db.

    pass


def cr(cid):
    pass


if __name__ == '__main__':
    for i in range(1, 11):
        if i == 1:
            print '==== 1st Calculation ===='
        elif i == 2:
            print '==== 2nd Calculation ===='
        elif i == 3:
            print '==== 3rd Calculation ===='
        else:
            print '==== {0}th Calculation ===='.format(i)
        new_ur = []
        for uid in db.uid:
            new_ur.append(ur(uid))
        for aur in new_ur:
            print aur
        db.user_rank = new_ur
