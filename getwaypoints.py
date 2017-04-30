#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys

url_file = open(sys.argv[1], 'r')

while 1:
    url = url_file.readline()
    if url == '':
        break
    a = url.split('https://www.google.mg/maps/dir/')[1]
    b = a.split('@')[0]
    c = b.split('/')
    for i in c:
        if i != '':
            i = i.replace("+-", "-")
            i = i.replace("'", "")
            print i

url_file.close()
