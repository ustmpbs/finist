# -*- coding: utf-8 -*-
"""
Created on Sun May 10 14:11:45 2020

@author: Davit
"""

# Import libraries
import pandas as pd
import numpy as np
import os


# new data for balancing
discount = pd.read_excel("balancing.xlsx", sheet_name = 'discount')
discount = discount.set_index('acronym')

limits = pd.read_excel("balancing.xlsx", sheet_name = 'limits')
limits = limits.set_index('limits')                         

la = pd.read_excel("balancing.xlsx", sheet_name = 'LA')
la = la.set_index('name')

# ===================================================================================================

def calc_balance(Current_period):
    
    # рассчитывает баланс в каждый период времени
    # если в ячейке столбца "formula_exec" стоит формула, то он ее рассчиывает
    # если стоит 'SUM по иерархии', то суммируются компоненты, входящие в эту переменную
    # если стоит 'MAX по иерархии', то выбирается максимальное значениние по иерархии
    
    A.loc['Assets_total', Current_period] = 0
    A.loc['Liab_total', Current_period] = 0
    
    for item in B_struct_exec.index:
        #print(item)
        if B_struct_exec.loc[item, 'Order']== 0:
            if B_struct_exec.loc[item, 'formula_exec'].startswith('if'):
                exec(B_struct_exec.loc[item, 'formula_exec']) 
            else:
                exec("A.loc['" + item + "', Current_period] = " + B_struct_exec.loc[item, 'formula_exec'])
        elif B_struct_exec.loc[item, 'formula_exec'] == 'SUM по иерархии':
            A.loc[item, Current_period] = A.loc[B_struct_exec.loc[item, 'Internal'].split(' '), Current_period].sum()
        else:
            A.loc[item, Current_period] = A.loc[B_struct_exec.loc[item, 'Internal'].split(' '), Current_period].max()


difference = abs(A.loc['Assets_total', 'T1'] - A.loc['Liab_total', 'T1'])


# temp variable
Previous_period = 'T0'


difference = abs(A.loc['Assets_total', 'T1'] - A.loc['Liab_total', 'T1'])

def shares_of_la(time, diff):
    
    # рассчитывает доли ликвидных активов, в которые должны быть инвестированы средства в слуаче, если пассивы больше активов
    # присваивает значения переменным с префиксом "Bal_"
    # рассчитвыает баланс заново
    la['shares_assets'] = ''
    summ = A.loc[la.index, Previous_period ].sum()
    for x in la.index:
        la.loc[x, 'shares_assets'] = A.loc[x, Previous_period]/ summ
        if la.loc[x, 'hla_id'] == 1:
            if x.startswith('CBR'):
                row = ["Bal_" + x]
            else:
                row = ["Bal_" + x[0].lower()+x[1:]]
            A.loc[row, time] = la.loc[x, 'shares_assets'] * diff
        else:
            A.loc[x, time] += diff * la.loc[x, 'shares_assets']
    calc_balance(time)

shares_of_la('T1', difference)

def step1(time, diff):
    
    # выполняет шаг 1 из алгоритма балансировки (сокращение ВЛА)
    # рассчитывает в предыдущий момент времени доли ликвидных активов, из которых средства будут вычитаться
    # рассчитывает предел ликвидных средств
    # присваивает значения переменным с префиксом "Bal_" со знаком "-" (минус)
    # перерассчиыват остаток разницы между активами и пассивами
    
    Bal_hla = min(diff, max(0, A.loc['Liq_assets', time] - limits.loc['Limit_Min_Liq_r', time] * A.loc['Liq_assets', time]))
    la['shares_liab'] = ''
    summ = A.loc[la[la['hla_id'] == 1].index, Previous_period ].sum()
    for x in la[la['hla_id'] == 1].index:
        la.loc[x, 'shares_liab'] = A.loc[x, Previous_period]/ summ
        if x.startswith('CBR'):
            row = ["Bal_" + x]
        else:
            row = ["Bal_" + x[0].lower()+x[1:]]
        A.loc[row, 'value'] = la.loc[x, 'shares_liab'] * Bal_hla * (-1)
        diff -= Bal_hla
        return diff



def step2(time, diff):
    
    # выполняет 2 шаг алгортма балансировки (заимствования у команий-резидентов)
    # рассчиывает лимит заимствования у резидентов в пределах группы
    # присваивает значения переменной с префиксом "Bal_"
    # перерасчиывает лимит
    # перерасчитывает остаток разницы между активами и пассивами 
    
    Bal_borrow_resid  = min(diff, limits.loc['Limit_Borrow_resid', time])
    A.loc['Bal_borrow_resid_rub', time] = Bal_borrow_resid
    limits.loc['Limit_Borrow_resid', time] -= Bal_borrow_resid
    diff -= Bal_borrow_resid
    return diff


def step3(time, diff):
    
    # выполняет 3 шаг алгортма балансировки (заимствования у команий-нерезидентов)
    # рассчитвает лимит  объема заимствования у компаний нерезидентов в пределах группы
    # присваивает значения переменной с префиксом "Bal_"
    # перерасчиывает лимит
    # перерасчитывает остаток разницы между активами и пассивами 
    
    Bal_borrow_foreign = min(diff, limits.loc['Limit_Borrow_foreign', time])
    A.loc['Bal_bank_borrow_foreign_cur', time] = Bal_borrow_foreign
    limits.loc['Limit_Borrow_foreign', time] -= Bal_borrow_foreign
    diff -= Bal_borrow_foreign
    return diff


def step4(time, diff):
    
    # выполняет 4 шаг алгортма балансировки (заимствования у Банка России)
    # рассчитвает лимит  объема заимствования у Банка России
    # присваивает значения переменной с префиксом "Bal_"
    # перерасчиывает лимит
    # перерасчитывает остаток разницы между активами и пассивами 
    
    Bal_borrow_CBR = min(diff, limits.loc['Limit_Borrow_CBR', time])
    A.loc['Bal_CBR_borrow_rub', time] = Bal_borrow_CBR
    limits.loc['Limit_Borrow_CBR', time] -= Bal_borrow_CBR
    diff -= Bal_borrow_CBR
    return diff
 
    
    
def step5(time, diff):
    
    # выполняет 5 шаг алгортма балансировки (заимствования на рынке МБК по РЕПО)
    # случайным образом присвоено значение переменной "Already_repo". В дальнейшем будет написан код его рассчета
    # рассчитывает лимит бумаг, которые могут заложены по сделкам РЕПО, 
    #        с учетом дисконта по каждому виду бондов и акций, 
    #        а также с учетом бумаг, уже находящихся в залоге.
    # присваивает значения переменной с префиксом "Bal_"
    # перерасчитывает остаток разницы между активами и пассивами
     
    Already_repo = 100000
    portf = 0
    for x in discount.index:
       estim = A.loc[x, time] * (1 - discount.loc[x, 'disc_value'])
       portf += estim
    limit_repo = portf - Already_repo
    Funds_raised_repo = min(diff, limit_repo)
    
    A.loc['Bal_bank_borrow_resid_rub', time] += 0.5*Funds_raised_repo
    A.loc['Bal_bank_borrow_resid_cur', time] += 0.5*Funds_raised_repo
    diff -= Funds_raised_repo
    return diff

# определяет допустимый уровень погрешности, в пределах которого различия между активами и пассивами игнорируются
tolerance = 10    
    
# перечень названий функций балансировщика, на которые я буду ссылаться
steps = ['step1(time, difference)', 'step2(time, difference)', 'step3(time, difference)', 'step4(time, difference)', 'step5(time, difference)']


def balancing(time):
    
    # производит непосредственно балансировку согласно алгоритму
    differ = A.loc['Assets_total', time] - A.loc['Liab_total', time]  
    difference = abs(differ)
    if differ < 0:  
        
        # в случае превалирования пассивов над активами достаточно всего одной итерации, чтобы достичь равентсва
        # потому что абсолютно вся разница была разбита на ВЛА, соответственно на второй итерации разница между активами и пассивами будет нулевой
        
        shares_of_la(time, difference)
        calc_balance(time)
    else:
        
        # в случае превалирования активов над пассивами будут поэтапно выполняться шаги из алгоритма балансировки, пока вся разница не нивелируется
        
        k = 0
        while difference > tolerance and k<=4:
            # выполняет функцию i из списка "steps"
            difference = eval(steps[k])
            k += 1
            if difference > tolerance and k>4:
                print('Кредитная организация имеет признаки технического дефолта')
                break
            else: 
                calc_balance(time)
       
