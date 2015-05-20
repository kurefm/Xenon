# -*- coding: utf-8 -*-

import json
import requests.models


s="""
cannanan@163.com----wwee27
canounuo24592425@163.com----wwee27
canouqunya051@163.com----wwee27
canpangshang7845@163.com----wwee27
canpatuo79894@163.com----wwee27
canpiaobi22325@163.com----wwee27
canqianzhizhan@163.com----wwee27
canshanpou5@163.com----wwee27
canshi441399@163.com----wwee27
canshijiuweng@163.com----wwee27
"""


account_str_list = s.split()
account_list=[]

for account_str in account_str_list:
    account=account_str.split('----')
    account_list.append((account[0],account[1]))


print account_list

# account_list = []
#
# for i in range(1, 21):
#     account = {'username': 'xenon{0:0>4}@163.com'.format(i), 'password': 'xenon.{0:0>4}'.format(i)}
#     account_list.append(account)
#
# with open('accounts', 'wb') as f:
#     j = json.dump(account_list, f)

# with open('accounts', 'rb') as f:
#     j = json.load(f)
#     print j[0]['username']
