# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:14:30 2020

@author: Davit
"""

import pandas as pd
import numpy as np
import os

os.chdir(r"D:\Bank of Russia\finist\compile")

portf_corp = ['low', 'large', 'mid', 'micro', 'sl_construct', 'sl_other', 'res']
portf_ind = ['mort', 'auto', 'card', 'consume']
depos_corp = ['gov', 'resid', 'foreign']
depos_ind= ['']
time = ['1D', '3M', '1Y', '2Y', '5Y', '10Y']

currency = ['rub', 'cur']


# =========================================================================================
# uploading data for PM

from_paramf = pd.read_excel('Product_module.xlsx', sheet_name = 'From_paramF')
from_paramd = pd.read_excel('Product_module.xlsx', sheet_name = 'From_paramD')
diction  = pd.read_excel('Product_module.xlsx', sheet_name = 'dict')
diction = diction.set_index("var")


#ParamD = pd.read_excel("Dave_finist.xlsx", sheet_name = "ParamD")
#ParamD = ParamD.set_index("name")
#
#ParamF = pd.read_excel("Dave_finist.xlsx", sheet_name = "ParamF")
#ParamF = ParamF.set_index("name")

# =========================================================================================
# craeting all vars by replacing

my_dict = {}
my_dict['item1'] = portf_corp
my_dict['item2'] = portf_ind
my_dict['item3'] = depos_corp
my_dict['item4'] = depos_ind
my_dict['item5'] = time



for port in portf_corp:
    for cur in currency:
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    