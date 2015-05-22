# -*- coding: utf-8 -*-

import json
import sys
import time
import crawler
import data
import common
from crawler import MobileWeiboCrawler
import errors
import packages.requests as requests
import argparse

SEARCH_PAGE_ERROR_WAIT = common.SEARCH_PAGE_ERROR_WAIT

CRAWLER_LIST = []
IDLE_CRAWLER = []


def read_account_list(filename):
    with open('accounts', 'rb') as f:
        return json.load(f)


def init_crawler_list():
    for account in read_account_list('accounts'):
        crawler_obj = MobileWeiboCrawler(account['username'], account['password'])
        IDLE_CRAWLER.append(crawler_obj)
        CRAWLER_LIST.append(crawler_obj)
        break


def show(*args, **kwargs):
    if not args:
        print_error('Nothing to show.')
        return
    elif args[0] == 'crawler':
        for crawler_obj in CRAWLER_LIST:
            print crawler_obj.username


def check(*args, **kwargs):
    for crawler_obj in CRAWLER_LIST:
        print '{0:<35}{1}'.format(crawler_obj.username, crawler_obj.check_login_status())


def insert(weibo_obj):
    data.insert_weibo(weibo_obj)
    print_info(u'Insert weibo {0} ok. Context is {1}'.format(weibo_obj.mid, weibo_obj.content))


def search(*args, **kwargs):
    if not args:
        print_error(u'Nothing to search.')
        return
    else:
        key = args[0]
        if args[0] == 'hotword':
            try:
                print_info(u'Get hot words.')
                key = IDLE_CRAWLER[0].get_host_word()[0]
            except errors.GetHostWordsError as ghwe:
                print_error(u"Can't get hot words. {0}".format(ghwe.args))
                return
        page = 1
        while (1):
            try:
                print_info(u'Search {0}'.format(key))
                IDLE_CRAWLER[0].search(key, handler=insert, start_at=page)
                print_info(u'Search finish')
                return
            except errors.SearchPageError as spe:
                page = spe.error_page
                print_error(u'Error in page {0}'.format(spe.error_page))
                print_info(u'Waiting {0} seconds'.format(SEARCH_PAGE_ERROR_WAIT))
                time.sleep(SEARCH_PAGE_ERROR_WAIT)


def print_info(text):
    text = text if isinstance(text, unicode) else text.decode('utf-8')
    print 'INFO: ', text.encode(sys.getfilesystemencoding(), 'ignore')


def print_error(text):
    text = text if isinstance(text, unicode) else text.decode('utf-8')
    print 'ERROR: ', text.encode(sys.getfilesystemencoding(), 'ignore')


COMMAND = {
    'show': show,
    'check': check,
    'search': search,
}

if __name__ == '__main__':
    print '########## Start up Xenon ##########'
    print_info('Loading account')
    print_info('Creating crawler')
    init_crawler_list()
    print_info('Crawler init finish')
    # init_crawler_list()
    while (1):
        command = raw_input('XENON>').decode(sys.getfilesystemencoding()).lower().strip()

        if command == 'exit':
            break
        command = command.split()

        try:
            COMMAND[command[0]](*tuple(command[1:]))
        except KeyError:
            print_error('Unknown command %s' % command[0])
