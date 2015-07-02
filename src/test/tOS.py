# -*- encoding: utf-8 -*-

import os

w=os.walk('.')

for a,b,c in w:
    print a,b,c