# -*- coding: utf-8 -*-
"""
Created on Sun May 10 14:11:42 2020

@author: Davit
"""

import pandas as pd
import numpy as np
import os


# Combine list of strings into a single one 
def list_to_string(l):
   return ' '.join(str(x) for x in l) 

def formula_split2(s):
    temp2 = ''
    while len(s)>0:
        temp = s[:s.find(']')+1]
        s = s[s.find(']')+1:]
        while not(temp[0].istitle()) and (temp.find(']')>0):
            temp=temp[1:]
        temp2 +=temp+' '
        if s.find(']')== -1: s=''
    temp2 = temp2.replace('[T-1]','_L').replace('[t0]','_O').replace('[T]','')
    temp3 = temp2.split(' ')[:-1]
    return list(set([x for x in temp3 if x.find('=')<0]))

def esli(s, z):
    uslovie = s[s.find('('):s.find(';')][1:]
    temp1234 = s[s.find(';'):][1:-1]
    result1=temp1234[:temp1234.find(';')]
    result2=temp1234[temp1234.find(';')+1:]
    
    temp1234 = "if ("+uslovie+"): \n    A.loc['"+z+"', Current_period] = "+result1+" \nelse: \n    A.loc['"+z+"', Current_period] = "+result2
    return temp1234


