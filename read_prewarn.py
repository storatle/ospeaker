#!/usr/bin/env python3
# -*- coding: utf-8 -*-


idx = 0
#nums = pre_db.read_start_numbers()
nums = [{'id':1,'number':'12'},{'id':2,'number':'tull'},{'id':3,'number':'44'},{'id':4,'number':50}]
for num in nums:
    if idx < num['id']:
        idx = num['id']
        try:
            start_num = int(num['number'])
            print(start_num)
        except:
            str_num = num
            print('No numbers!')





