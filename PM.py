# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 12:00:44 2020

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


ParamD = pd.read_excel("Dave_finist.xlsx", sheet_name = "ParamD")
ParamD = ParamD.set_index("name")

ParamF = pd.read_excel("Dave_finist.xlsx", sheet_name = "ParamF")
ParamF = ParamF.set_index("name")

# =========================================================================================
# craeting all vars by replacing

my_dict = {}
my_dict['item1'] = portf_corp
my_dict['item2'] = portf_ind
my_dict['item3'] = depos_corp
my_dict['item4'] = depos_ind
my_dict['item5'] = time

data_f = []

for j in from_paramf.index:
    d = 0
    while diction.index[d] not in from_paramf.loc[j, 'name_acronym']:
        d += 1
    temp = my_dict[diction.loc[diction.index[d], 'list']]
    for i in range(len(temp)):
        for k in range(len(currency)):
            data_f.append(from_paramf.loc[j, 'name_acronym'].replace('%портфель%', temp[i]).replace('%валюта%', currency[k]).replace("__", '_'))

data_f = pd.DataFrame(data_f).rename(columns={0: "name"})
  
data_d = []

for j in from_paramd.index:
    d = 0
    while diction.index[d] not in from_paramd.loc[j, 'name_acronym']:
        d += 1
    temp =  my_dict[diction.loc[diction.index[d], 'list']]
    for i in range(len(temp)):
        for k in range(len(currency)):
            if diction.index[d] != 'XX':
                data_d.append(from_paramd.loc[j, 'name_acronym'].replace('%портфель%', temp[i]).replace('%валюта%', currency[k]).replace("__", '_').replace('(deposit)', ''))
            else:
                data_d.append(from_paramd.loc[j, 'name_acronym'].replace('XX', temp[i]))

data_d = pd.DataFrame(data_d).rename(columns={0: "name"})

# =========================================================================

Period = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8' ]

for time in Period:
    data_f[time] =''
    data_d[time] =''
data_f = data_f.set_index('name')
data_d = data_d.set_index('name')


for i in data_f.index:
    data_f.loc[i, 'T0'] = ParamF.loc[i, 'value']
    
for i in data_d.index:
    data_d.loc[i, 'T1'] = ParamD.loc[i, 'T1']

Current = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']
Previous = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
time='T2'



def prod_mod_cred_le(time):
    k = 0
    while time != Current[k]:
        k += 1
    Previous_period = Previous[k]
    
    period_t = k +1 
    
    for port in portf_corp:
        for cur in currency:
            
            # расчет npl
            npl = (data_f.loc['C_loan_' + port +'_good_portf_'+ cur, Previous_period] * data_d.loc['PD_good_C_loan_' + port + '_' + cur, time]  +
                   data_f.loc['C_loan_' + port +'_good_off_'+ cur, Previous_period] * data_d.loc['PD_good_C_loan_' + port + '_' + cur, time] * 0.02)/4  # insert ccf instead of 0.02
            
                   
            # расчет выгашивания
            duration = data_f.loc['Duration_C_loan_' + port + '_' + cur, time]/0.25
            if duration  >= period_t:
                t = int(duration)
                repayments =  data_d.loc['New_loans_C_loan_' + port + '_' + cur, Current[k - t]]  # check out the formula, guess there is an error
            else:
                repayments = 0
            
            # работающие кредиты для каждого из портфелей  
            # проверить и дописать
            data_f.loc['C_loan_' + port + '_good_portf_'+ cur, time]= data_f.loc['C_loan_' + port + '_good_portf_'+ cur, Previous_period] - npl + data_d.loc['New_loans_C_loan' + port + '_' + cur, time] - data_d.loc['Repayment_C_loan_' + port + '_' + cur, time ] - repayments
            
            # работающие кредиты по нкл
            balancirov = 1000 # нужно уточнить формулу
            data_f.loc['C_loan_' + port + '_good_off_' + cur, time] = data_f.loc['C_loan_' + port +'_good_portf_'+ cur, time] * data_f.loc['C_loan_' + port + '_good_off_' + cur, Previous_period]/data_f.loc['C_loan_' + port +'_good_portf_'+ cur, Previous_period] + balancirov
            
            # Резервы по работающим кредитам
            data_f.loc['C_loan_'+port+'_good_prov_'+cur, time] = data_f.loc['C_loan_'+port+'_good_portf_'+cur, time] * data_d.loc['Prov_good_C_loan_'+port+'_'+cur, time] * (-1)
            
            # Неработающие кредиты
            data_f.loc['C_loan_' + port + '_npl_portf_' + cur, time] = data_f.loc['C_loan_' + port + '_npl_portf_' + cur, Previous_period] + npl
            
            # Резервы по нарботающим кредитам
            data_f.loc['C_loan_'+port+'_npl_prov'+cur, time] = data_f.loc['C_loan_'+port+'_npl_portf'+cur, time] * data_d.loc['Prov_NPL_C_loan_'+port+'_'+cur, time] * (-1)
            
            
    
    
def prod_mod_cred_fl(time):
    k = 0
    while time != Current[k]:
        k += 1
    Previous_period = Previous[k]

    for port in portf_ind:
        for cur in currency:
            
            # расчет актуальной ставки по кредитам ФЛ
            yield_growth = 0.5 # уточнить потом, что это значит, откуда брать?
            data_f.loc['Int_rate_act_Ind_loan_' + port + '_' + cur, time] = data_f.loc['Int_rate_act_Ind_loan_' + port + '_' + cur, Previous_period] + (yield_growth + ParamD.loc[rating+'_spread_'+cur, time])/100
            int_rate = data_f.loc['Int_rate_act_Ind_loan_' + port + '_' + cur, time]
        
     
    
    
def prod_mod_dep_le(time):
    k = 0
    while time != Current[k]:
        k += 1
    Previous_period = Previous[k]
    
    for dep in depos_corp:
        for cur in currency:
            
            # портфель депозитов
            repayments_new_C_dep = 1000 #уточнить
            balance = 1000 # уточнить
            data_f.loc['C_deposit_'+dep+ '_'+cur, time ] = data_f.loc['C_deposit_'+dep+ '_'+cur, Previous_period] + ParamD.loc['New_C_loan_deposit_' + dep + '_'+cur, time] - ParamD.loc['Repayments_C_deposit_' + dep + '_' + cur, time] - repayments_new_C_dep + balance 
    
    
    
    
    
    
    
    
    





