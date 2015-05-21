# coding=utf-8
# __author__ = '国豪'

import MySQLdb
import time
from models import *
from common import CONFIG
import _mysql_exceptions

__HOST = CONFIG.DB.host
__DB = CONFIG.DB.db
__USER = CONFIG.DB.user
__PASSWD = CONFIG.DB.passwd
__CHARSET = CONFIG.DB.charset


def MysqlConnector():
    """
    使用了上面的我全局变量来进行操作
    主要的就是 global 没有什么难度
    @return: 返回的是一个conn的链接对象
    """
    global __HOST
    global __USER
    global __PASSWD
    global __DB
    global __CHARSET
    return MySQLdb.connect(user=__USER, passwd=__PASSWD, host=__HOST, db=__DB, charset=__CHARSET);


def insert_basic_function(sql, args):
    conn = None
    cursor = None
    try:
        #   使用全局变量的时候要注意了
        # conn= MySQLdb.connect(user='root',passwd='xenon',host='192.168.40.128',db='XenonData',charset="utf8")
        conn = MysqlConnector()
        cursor = conn.cursor()
        cursor.execute(sql, args)
        conn.commit()

    except _mysql_exceptions.DatabaseError as dbe:
        raise dbe

    finally:
        cursor.close()
        conn.close()


# 用户表
def insert_users(weibo_user):
    sql = """INSERT INTO Users (uid,nickname,job,address,fans_num) VALUES(%s,%s,%s,%s,%s) on duplicate KEY UPDATE nickname=values(nickname),job=values(job),address=values(address),fans_num=values(fans_num)"""
    args = (weibo_user.uid, weibo_user.nickname, weibo_user.job, weibo_user.address, weibo_user.fans_num)
    insert_basic_function(sql, args)


# 微博表
def insert_weibo(Weibo):
    sql = """INSERT INTO Weibo(mid, content, posttime, time_stamp, extra, forward_num, comment_num, like_num) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) on duplicate KEY UPDATE content=VALUES(content),posttime=VALUES(posttime),time_stamp=VALUES(time_stamp),extra=VALUES(extra),forward_num=VALUES(forward_num),comment_num=VALUES(comment_num),like_num=VALUES(like_num)"""
    args = (str(Weibo.mid), Weibo.content, Weibo.time, Weibo.timestamp, Weibo.extra, Weibo.forward_num, Weibo.comment_num,
            Weibo.like_num)
    insert_basic_function(sql, args)
    __insert_user_weibo(Weibo.uid,Weibo.mid)


#   评论表
def insert_comments(WeiboComment):
    sql = """"""

    """
    以下的函数都是在插入微博，用户，评论的时候被调用
    """


#   用户微博关系表
def __insert_user_weibo(uid, mid):
    sql = """INSERT IGNORE INTO user_weibo(uid, mid) VALUES (%s,%s)"""
    args = (uid, mid)
    insert_basic_function(sql, args)


# 用户评论关系表
def __insert_user_comment(uid, cid):
    sql = """INSERT IGNORE INTO user_comment(uid,cid) VALUES (%s,%s)"""
    args = (uid, cid)
    insert_basic_function(sql, args)


# 微博评论关系表
def __insert_weibo_comment(mid, cid):
    sql = """INSERT IGNORE INTO weibo_comment(mid,cid) VALUES(%s,%s)"""
    args = (mid, cid)
    insert_basic_function(sql, args)


# 用户关注用户 关系表 A 关注 B
def __insert_Follow(uidA, uidB):
    sql = """INSERT IGNORE INTO Follow(uidA,uidB) VALUES(%s,%s)"""
    args = (uidA, uidB)
    insert_basic_function(sql, args)


# 微博转发关系表 A 转发 B
def __insert_Forward(midA, midB):
    sql = """INSERT IGNORE INTO Forward(midA,midB) VALUES (%s,%s)"""
    args = (midA, midB)
    insert_basic_function(sql, args)


# 微博-用户点赞 关系表（一条微博用哪些用户点赞）
def __insert_weiboPL(mid, uid):
    sql = """INSERT IGNORE INTO weibo_PL(mid,uid) VALUES(%s,%s)"""
    args = (mid, uid)
    insert_basic_function(sql, args)


# 评论用户点赞 关系表（一条评论有哪些用户点赞）
def __insert_commentPL(cid, uid):
    sql = """INSERT IGNORE INTO comment_PL(cid,uid) VALUES(%s,%s)"""
    args = (cid, uid)
    insert_basic_function(sql, args)


if __name__ == '__main__':

    # user = WeiboUser(335464,'lOG的风格回家O','stu','baoza')
    # weibo = Weibo(uid='23236',mid='132113',content='你好',time= time.ctime(),timestamp= time.ctime())
    #
    # start = time.time()
    # print 'basic',time.time()-start
    conns = MysqlConnector()
    cursors = conns.cursor()
    cursors.execute('select * FROM Forward')
    # cursor.execute('show tables')
    result = cursors.fetchall()
    if result:
        print result
