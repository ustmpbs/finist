# -*- coding: utf-8 -*-
"""
Created on Sun May 10 14:05:20 2020

@author: Davit
"""

import pandas as pd
import numpy as np
import os


path = r"D:/Bank of Russia/finist/compile"
os.chdir(path)

regn = int(input('Введите рег. номер банка: '))
date = str(input('Введите дату расчета: '))
horison = int(input('Введите горизонт планирования: '))

# ================================================================================================

# Import data
B_struct = pd.read_excel (r'Dave_finist.xlsx', sheet_name='Struct')
B_struct = B_struct.set_index('name')

Exter = pd.read_excel("Dave_finist.xlsx", sheet_name = "Exter")
Exter = Exter.set_index("name")

ParamD = pd.read_excel("Dave_finist.xlsx", sheet_name = "ParamD")
ParamD = ParamD.set_index("name")

ParamF = pd.read_excel("Dave_finist.xlsx", sheet_name = "ParamF")
ParamF = ParamF.set_index("name")

rating = ParamF.loc['Bank_rating', 'value']
# ================================================================================================

# running subfiles
runfile(path+'/functions.py', wdir = path)

runfile(path+'/Data_preparation.py', wdir = path)

#runfile(path+'/PM.py', wdir = path)

runfile(path+'/balancing module.py', wdir = path)

# ============================================================================================================


# main calculations
for i in ['T1']: 
    
    # нахождение предыдушего периода в зависимости от текущего
    k = 0
    while i == Current[k]:
        k += 1
    Previous_period = Previous[k]
    
    #data from product engine 
    add_prod(i)
    # calc balance
    calc_balance(i)
    
    # calculating difference between assets and liabilities
    differ = A.loc['Assets_total', i] - A.loc['Liab_total', i]          
    difference = abs(differ)
    
    # balancirovka
    iteration = 0
    while difference > tolerance:
        balancing(i)
        differ = A.loc['Assets_total', i] - A.loc['Liab_total', i]          
        difference = abs(differ)
        iteration += 1
    






