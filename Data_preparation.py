# -*- coding: utf-8 -*-
"""
Created on Sun May 10 14:11:43 2020

@author: Davit
"""

import pandas as pd
import numpy as np
import os

B_struct['formula'] = B_struct['formula'].apply(lambda x: x if (x in ['nothing', 'balancing', 'SUM по иерархии', 'External', 'SUM a) по иерархии', 'SUM b) по иерархии', 'SUM c) по иерархии', 'SUM d) по иерархии', 'SUM e) по иерархии', 'МАКС по иерархии' ]) else x.replace('МАКС','max').replace('МИН','min'))

# Identify components of all formulas
B_struct['Components'] = B_struct['formula'].apply(lambda x: np.nan if (x in ['nothing', 'balancing', 'SUM по иерархии', 'External', 'SUM a) по иерархии', 'SUM b) по иерархии', 'SUM c) по иерархии', 'SUM d) по иерархии', 'SUM e) по иерархии', 'МАКС по иерархии' ]) else list_to_string(formula_split2(x))) 
 
   
# Identify components of all aggregated accounts (SUM по иерархии)
B_struct['Internal'] = ''
B_struct['Internal'] = np.where(B_struct['formula'] == 'SUM по иерархии', 
    B_struct['hierarchy_fmod'].apply(lambda x: '' if (str(x) == 'nan' or str(x) == '0') else list_to_string(B_struct.loc[B_struct['hierarchy_fmod'].str.startswith(x) & (B_struct['hierarchy_fmod'].str.count('.') == 2*(x.count('.') + 1)) & (B_struct['hierarchy_fmod'] != x), ].index)), B_struct['Internal'])

# заглушки для формул с двузначными числами
B_struct['Internal'] = np.where(B_struct['formula'] == 'SUM по иерархии', np.where( B_struct['hierarchy_fmod'].str.contains(pat = '10'),
    B_struct['hierarchy_fmod'].apply(lambda x: '' if (str(x) == 'nan' or str(x) == '0') else list_to_string(B_struct.loc[B_struct['hierarchy_fmod'].str.startswith(x) & (B_struct['hierarchy_fmod'].str.count('.') == 1 + 2*(x.count('.') + 1)) & (B_struct['hierarchy_fmod'] != x), ].index)), B_struct['Internal']), B_struct['Internal'])

B_struct['Internal'] = np.where(B_struct['formula'] == 'SUM по иерархии', np.where( B_struct['hierarchy_fmod'].str.contains(pat = '12'),
    B_struct['hierarchy_fmod'].apply(lambda x: '' if (str(x) == 'nan' or str(x) == '0') else list_to_string(B_struct.loc[B_struct['hierarchy_fmod'].str.startswith(x) & (B_struct['hierarchy_fmod'].str.count('.') == 1 + 2*(x.count('.') + 1)) & (B_struct['hierarchy_fmod'] != x), ].index)), B_struct['Internal']), B_struct['Internal'])


# формирование переменных для "МАКС по иерархии"
B_struct['Internal'] = np.where(B_struct['formula'] == 'МАКС по иерархии',
        B_struct['hierarchy_fmod'].apply(lambda x: '' if (str(x) == 'nan' or str(x) == '0') else list_to_string(B_struct.loc[B_struct['hierarchy_fmod'].str.startswith(x) & (B_struct['hierarchy_fmod'].str.count('.') == 1 + 2*(x.count('.') + 1)) & (B_struct['hierarchy_fmod'] != x), ].index)), B_struct['Internal'])


B_struct['Order'] = np.where(B_struct['Internal'] == '', 0 , np.nan)

while any(B_struct['Order'].isnull()):
    for i in B_struct.loc[B_struct['Order'].isnull()].index:  
        a = B_struct.loc[str(B_struct.loc[i, 'Internal']).split(' '), 'Order']
    #    print(a)
        if not(np.isnan(a).any()):
            B_struct.loc[i, 'Order'] = max(a) + 1
  

B_struct['formula_exec'] = B_struct['formula']
for i in B_struct.loc[B_struct['Components'].notnull()].index:
    s = B_struct.loc[i, 'formula']
    if s.startswith('ЕСЛИ'):
        s = esli(s, i)
    if B_struct.loc[i, 'from_list'] != np.nan and 'ParamF' in B_struct.loc[i, 'from_list']:
        for x in B_struct.loc[i, 'Components'].split(' '):
            if x in ParamF.index and not x.startswith('N1') or x.startswith('Non') and not x.endswith('pp'):
                s = s.replace(x + "[T]", "ParamF.loc['" + x +"', 'value']") 
                s = s.replace(x + "[T-1]", "ParamF.loc['" + x +"', 'value']")
            else: 
                if x.endswith('level') or x.endswith('growth') or x.endswith('ch') or x.endswith('level_rub') or x.endswith('level_cur') or x.endswith('volume') or x in ParamD.index or x.endswith('level_L'):
                    s = s.replace(x + "[T]", "ParamD.loc['" + x +"', Current_period]") 
                    s = s.replace(x + "[T-1]", "ParamD.loc['" + x +"', Previous_period]")
                elif x.endswith('_L'):
                    x = x.replace('_L', '')
                    s = s.replace(x + "[T-1]", "A.loc['" + x + "_L', Current_period]")
                elif x.endswith('_D'):
                    s = s.replace(x + '_D', "A.loc['" + i + "', 'T0']")
                else:
                    s = s.replace(x + "[T]", "A.loc['" + x + "', Current_period]")
    else:       
        for x in B_struct.loc[i, 'Components'].split(' '):        
            if x.endswith('level') or x.endswith('growth') or x.endswith('ch') or x.endswith('level_rub') or x.endswith('level_cur') or x.endswith('volume') or x in ParamD.index or x.endswith('level_L'):
                s = s.replace(x + "[T]", "ParamD.loc['" + x +"', Current_period]") 
                s = s.replace(x + "[T-1]", "ParamD.loc['" + x +"', Previous_period]")
            elif x.endswith('_L'):
                x = x.replace('_L', '')
                s = s.replace(x + "[T-1]", "A.loc['" + x + "_L', Current_period]")
            elif x.endswith('_D'):
                s = s.replace(x + '_D', "A.loc['" + i + "', 'T0']")
            else:
                s = s.replace(x + "[T]", "A.loc['" + x + "', Current_period]")
    B_struct.loc[i, 'formula_exec'] = s


# Create version of B_struct for execution in the main code
B_struct['bin'] = B_struct['formula_exec'].apply(lambda x: 0 if x in ['nothing', 'balancing', 'External', 'SUM a) по иерархии', 'SUM b) по иерархии', 'SUM c) по иерархии', 'SUM d) по иерархии', 'SUM e) по иерархии'] else 1 ) 
B_struct_exec = B_struct.loc[B_struct['bin'] == 1, ].sort_values('Order') 


fix_var = ["Income_other_deriv_result_rub", "Income_other_deriv_result_cur"]

for i in fix_var:
    B_struct_exec.loc[i, "formula_exec"] = B_struct_exec.loc[i, "formula_exec"].replace(i + "[T0]", "A.loc['" + i + "', 'T0']")

B_struct_exec['formula_exec'] = B_struct_exec['formula_exec'].apply(lambda x: x.replace('МАКС(', 'max(').replace('0,5', '0.5').replace(';', ',').replace("Capital_A.loc['", "ParamF.loc['Capital_").replace("_N1.1', Current_period", "_N1.1', 'value'").replace("_N1.2', Current_period", "_N1.2', 'value'").replace("_N1.0', Current_period", "_N1.0', 'value'") )



# находит переменные, заканчивающиеся на "_L", и меняет на "Previous_period"
# приводит в соответствие нотацию для подгрузки данных из листа "ParamF" из файла "Dave_finist"
for x in B_struct_exec.index:
    if "_L" in B_struct_exec.loc[x, 'formula_exec']:
         B_struct_exec.loc[x, 'formula_exec'] = B_struct_exec.loc[x, 'formula_exec'].replace("_L', Current_period", "', Previous_period")
    elif "Bal_" in B_struct_exec.loc[x, 'formula_exec']:
         B_struct_exec.loc[x, 'formula_exec'] = B_struct_exec.loc[x, 'formula_exec'].replace("Bal_A.loc['", "A.loc['Bal_")
    elif B_struct_exec.loc[x, 'formula_exec'] in ['Cred_line_Group_resid', 'Cred_line_Group_foreign', 'Cred_line_CBR']:
         B_struct_exec.loc[x, 'formula_exec'] = B_struct_exec.loc[x, 'formula_exec'] .replace(B_struct_exec.loc[x, 'formula_exec'], "ParamF.loc['" + B_struct_exec.loc[x, 'formula_exec'] + "', 'value']")
        
for x in B_struct_exec.index:
    if "_L" in B_struct_exec.loc[x, 'formula_exec']:
         B_struct_exec.loc[x, 'formula_exec'] = B_struct_exec.loc[x, 'formula_exec'].replace("_L', Current_period", "', Previous_period")
    elif "Bal_" in B_struct_exec.loc[x, 'formula_exec']:
         B_struct_exec.loc[x, 'formula_exec'] = B_struct_exec.loc[x, 'formula_exec'].replace("Bal_A.loc['", "A.loc['Bal_")
    elif B_struct_exec.loc[x, 'formula_exec'] in ['Cred_line_Group_resid', 'Cred_line_Group_foreign', 'Cred_line_CBR']:
         B_struct_exec.loc[x, 'formula_exec'] = B_struct_exec.loc[x, 'formula_exec'] .replace(B_struct_exec.loc[x, 'formula_exec'], "ParamF.loc['" + B_struct_exec.loc[x, 'formula_exec'] + "', 'value']")


B_struct_exec.loc['RWA_Credit_bal', 'formula_exec'] = "(A[Current_period] * A['RWA_coef']).sum()"

# Delete temporary variables
del a, i, s, x
# ================================================================================================


# лист с соответствующими значениями текущего и предыдущего периодов
Current = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']
Previous = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']


# Создает рабочую таблицу, где все будет собираться
B_struct['Start_value'] = 0
A = pd.DataFrame(data = B_struct['Start_value'].values, index = B_struct.index)
for i in Current:
    A[i]=0
A = A.rename(columns = {0: "T0"})

# загружает данные из листа "fmod" из файла "Dave_finist" данные на момент T0.
# в дальнейшем также будет разработан модуль подкачки данных на Т0     
for x in A.index:
    if x in ParamF.index:
        A.loc[x, 'T0'] = ParamF.loc[x, 'value']


for item in B_struct_exec.index:
        #print(item)
        if B_struct_exec.loc[item, 'formula_exec'] == 'SUM по иерархии':
            A.loc[item, 'T0'] = A.loc[B_struct_exec.loc[item, 'Internal'].split(' '), 'T0'].sum()

B_struct_exec.loc['Prov_ch_total_include_sec', 'formula_exec'] = B_struct_exec.loc['Prov_ch_total_include_sec', 'formula_exec'].replace('ParamD', 'A')

A['RWA_coef'] = B_struct['rwa_coef']

# ===========================================================================================


# upload initial values
def add_prod(time):
    
    # подкачивает данные из листа "Exter" из файла "Dave_finist"
    # является заглушкой продуктового модуля
    # данные вбиты случаным образом
    
    for i in Exter.index:
        A.loc[i, time] = Exter.loc[i, time]

