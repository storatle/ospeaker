#!/usr/bin/env python3
# -*- coding: utf-8 -*-



f = open('num.txt', 'r')
line = f.read()
nums = line.split(';')
for num in nums:
    try:
        start_num = int(num)
        print(start_num)
    except:
        str_num = num






