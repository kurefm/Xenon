# -*- coding: utf-8 -*-

import re
import timeit


def testRe(pattern, string, type='match'):
    reType = {
        'match': re.match,
        'search': re.search,
        'findall': re.findall
    }
    result = reType[type](pattern, string)
    if not result:
        raise Exception("Can't find %s" % string)


def runReTime(testTime=1000000):
    return timeit.timeit('forTest()','from __main__ import forTest', number=testTime)

string = 'sinaSSOController.preloginCallBack({"retcode":0,"servertime":1429888988,"pcid":"xd-fb1a4d986617776a7c112fcb7069dc4a89cb","nonce":"3L8F4R","pubkey":"EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443","rsakv":"1330428213","exectime":3})'

def forTest():
    result=re.match(r'[^{]+({.+?})',string)
    # result=re.search(r'({.+?})',string)
    if not result:
        raise Exception("Can't find %s" % string)

print runReTime(100000)
