# -*- coding: utf-8 -*-

import json
import crawler
import data
import common
from crawler import MobileWeiboCrawler
import argparse

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
        print_error('')
    if args[0] == 'crawler':
        for crawler_obj in CRAWLER_LIST:
            print crawler_obj.username


def check(*args, **kwargs):
    for crawler_obj in CRAWLER_LIST:
        print '{0:<35}{1}'.format(crawler_obj.username, crawler_obj.check_login_status())


def print_info(string):
    print 'INFO: ', string


def print_error(string):
    print 'ERROR:', string


COMMAND = {
    'show': show,
    'check': check,
}

if __name__ == '__main__':
    print 'Start up Xenon'
    print_info('Loading account')
    print_info('Creating crawler')
    init_crawler_list()
    print_info('Crawler init finish')
    # init_crawler_list()
    while (1):
        command = raw_input('XENON>').lower().strip()
        if command == 'exit':
            break
        command = command.split()
        try:
            COMMAND[command[0]](*tuple(command[1:]))
        except KeyError:
            print_error('Unknown command %s' % command[0])
