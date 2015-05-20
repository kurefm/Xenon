# -*- coding: utf-8 -*-
import json

s = """
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


def create_xenon_account(i, j):
    """from i to j."""
    acco_list = []
    for i in range(i, j + 1):
        acco = {'username': 'xenon{0:0>4}@163.com'.format(i), 'password': 'xenon.{0:0>4}'.format(i)}
        acco_list.append(acco)
    return acco_list


if __name__ == '__main__':
    account_str_list = s.split()
    account_list = []
    account_list.extend(create_xenon_account(1, 2))
    for account_str in account_str_list:
        account = account_str.split('----')
        account_list.append({'username': account[0], 'password': account[1]})
    print account_list
    with open('accounts', 'wb') as f:
        j = json.dump(account_list, f)
