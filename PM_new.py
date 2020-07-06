# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:14:30 2020

@author: Davit
"""

import pandas as pd
import numpy as np
import os

os.chdir(r"D:\Bank of Russia\finist\compile")

portf_corp = ['low_', 'large_', 'mid_', 'micro_', 'sl_construct_', 'sl_other_', 'res_']
portf_ind = ['mort_', 'auto_', 'card_', 'consume_']
depos_corp = ['gov_', 'resid_', 'foreign_']
depos_ind= ['']

bonds_type = ['FVPL_', 'FVOCI_', 'AMC_']
bonds_reg = ['gov_', 'corp_', 'foreign_']

time = ['1D', '3M', '1Y', '2Y', '5Y', '10Y']
currency = ['rub', 'cur']


# =========================================================================================
# uploading data for PM

from_paramf = pd.read_excel('Product_module.xlsx', sheet_name = 'From_paramF')
from_paramd = pd.read_excel('Product_module.xlsx', sheet_name = 'From_paramD')
diction  = pd.read_excel('Product_module.xlsx', sheet_name = 'dict')
diction = diction.set_index("var")

bal_ = pd.read_excel('balancing.xlsx', sheet_name = 'BAL_')
bal_ = bal_.set_index('name')

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

Period = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8' ]
Current = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']
Previous = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

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
data_f = data_f.set_index('name')

for time in Period:
    data_f[time] =''


for i in data_f.index:
    data_f.loc[i, 'T0'] = ParamF.loc[i, 'value']


def cred_le(time):
    
    k = 0
    while time != Current[k]:
        k += 1
    Previous_period = Previous[k]
    
    period_t = k +1
    
    for port in portf_corp:
        for cur in currency:
            
            # сумма прироста NPL по каждому портфелю
            npl_le = (data_f.loc['C_loan_' + port +'good_portf_'+ cur, Previous_period] * ParamD.loc['PD_good_C_loan_' + port + cur, time]  +
                   data_f.loc['C_loan_' + port +'good_off_'+ cur, Previous_period] * ParamD.loc['PD_good_C_loan_' + port + cur, time] * ParamD.loc['CCF', time])/4 

            # суммарный NPL с учетом прироста
            data_f.loc['C_loan_' + port + 'good_portf_' + cur, time] =  data_f.loc['C_loan_' + port + 'good_portf_' + cur, Previous_period] + npl_le
            
            # потрфель хороших долгов
            bal = 1000 # уточнить позднее переменную балансировщика
            pogash = 1000 # уточнмть поднее формулу погашения
            data_f.loc['C_loan_'+port+'good_portf_' + cur, time] = data_f.loc['C_loan_'+port+'good_portf_' + cur, Previous_period] - npl_le + ParamD.loc['New_loans_C_loan_'+port +cur, time] - ParamD.loc['Repayment_C_loan_'+ port + cur, time] + bal - pogash
    
            # НКЛ           
            data_f.loc['C_loan_'+port+'good_off_'+cur, time] = data_f.loc['C_loan_'+port+'good_off_'+cur, Previous_period] * data_f.loc['C_loan_'+port+'good_portf_' + cur, time] * ParamD.loc['Off_to_Bal_C_loan' + port + cur, time] / data_f.loc['C_loan_'+port+'good_portf_' + cur, Previous_period]
            
            # Резервы по хорошим долгам
            data_f.loc['C_loan_'+port+'good_prov_'+cur, time] = (-1) * data_f.loc['C_loan_'+port+'good_portf_' + cur, time] * ParamD.loc['Prov_good_C_loan_' + port +cur, time]
            
            # Портефель NPL
            data_f.loc['C_loan_' + port + 'npl_portf_' + cur, time] = data_f.loc['C_loan_' + port + 'npl_portf_' + cur, time] + npl_le
            
            # Резервы по портфелю NPL
            data_f.loc['C_loan_' + port + 'npl_prov_' + cur, time] = (-1) * data_f.loc['C_loan_' + port + 'npl_portf_' + cur, time] * ParamD.loc['Prov_MPL_C_loan_' + port + cur, time]
            
            # 
            act_rate = data_f.loc['Int_rate_act_C_loan_'+port + cur, Previous_period]
            
                        
def cred_fl(time):
    
    k = 0
    while time != Current[k]:
        k += 1
    Previous_period = Previous[k]
    
    period_t = k +1
    
    for port in portf_ind:
        for cur in currency:
            
            # прирост NPL
            npl_fl = (data_f.loc['Ind_loan_' + port + 'good_portf_' + cur, Previous_period] * ParamD.loc['PD_good_Ind_loan_' + port + cur, time] + data_f.loc['Ind_loan_' + port + 'good_off_' + cur, Previous_period] * ParamD.loc['PD_good_off_Ind_loan_' + port + cur, time] * ParamD.loc['CCF', time])/4
            
            # портфель хороших долгов
            repay_fl= 1000 # уточнить
            data_f.loc['Ind_loan_' + port + 'good_portf_' + cur, time] = data_f.loc['Ind_loan_' + port + 'good_portf_' + cur, Previous_period] - npl_fl + data_f.loc['New_loans_Ind_loan_'+port + cur, time] - data_f.loc['Repayment_Ind_loan_'+ port + cur, time] - repay_fl
            
            # Резервы по хорошим долгам
            data_f.loc['Ind_loan_' + port + 'good_prov_'+ rub, time] = data_f.loc['Ind_loan_' + port + 'good_portf_' + cur, time] * ParamD.loc['Prov_good_Ind_loan_' + port + cur, time]
            
            # портфель NPL
            data_f.loc['Ind_loan_'+port+'npl_portf_'+cur, time] = data_f.loc['Ind_loan_'+port+'npl_portf_'+cur, Previous_period] + npl_fl

            # Резервы по портфелю NPL
            data_f.loc['Ind_loan_' + port + 'npl_prov_' + cur, time] = data_f.loc['Ind_loan_'+port+'npl_portf_'+cur, time] * ParamD.loc['Prov_NPL_Ind_loan_' + port + cur, time]   
            
            

def dep_le(time):
    
    k = 0
    while time != Current[k]:
        k += 1
    Previous_period = Previous[k]
    
    period_t = k +1
    
    for dep in depos_corp:
        for cur in currency:
            
            # Объем депозитов
            data_f.loc['C_deposit_' + dep + cur, time] = data_f.loc['C_deposit_' + dep + cur, Previous_period] + data_f.loc['New_loans_C_deposit_' + dep + cur, time] - data_f.loc['Repayment_C_deposit_' + dep + cur, time]
            
            # ставка привлечения по депозитам ЮЛ
            
            # процентный расход по депозитам ЮЛ
            
        
def dep_fl(time):
    
    k = 0
    while time != Current[k]:
        k += 1
    Previous_period = Previous[k]
    
    period_t = k +1
    
    for cur in currency:
        
        # объем вкладов населения
        data_f.loc['Ind_deposit_' + cur, time] = data_f.loc['Ind_deposit_' + cur, Previous_period] + data_f.loc['New_loans_Ind_deposit_'+cur, time] + data_f.loc['Repayment_Ind_deposit_'+cur, time]
        
        # ставка привлечения по депозитам ЮЛ
        
        
        # процентный расход по депозитам ЮЛ
        
    
#==============================================================================================================
# процентный риск по торговому портфелю
        


def pm_bonds(time):
    
    for b_type in bonds_type:
        for b_reg in bonds_reg:
            for cur in currency:
                
                if cur == 'rub':
                    exch_rate = 1
                else:
                    exch_rate = ParamD.loc['Exch_rate', time]
                
                # объем облигаций
                A.loc['Bonds_' + b_type + b_reg  + cur, time] = A.loc['Bonds_' + b_type + b_reg + cur, Previous_period] * exch_rate * ParamD.loc['Bonds_' + b_type + b_reg + 'reval_' + cur, time] + bal_.loc['Bal_Bonds_' + b_type + b_reg  + cur, time]



    
    
    
    
    
