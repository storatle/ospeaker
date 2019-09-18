#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

def get_next_element(my_itr):
     try:
         return next(my_itr)
     except StopIteration:
         return None


my_li = [1, 2, 3, 4, 5]    
#convert the list to an iterator 
my_itr = iter(my_li)    
for i in range(0, 228):
    value = get_next_element(my_itr)
    if value is None:
        my_itr = iter(my_li)    
        value = get_next_element(my_itr)    
    print(value)  
