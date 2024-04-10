import pandas as pd
import os
from datetime import datetime as date

def get_path():
    print(os.path)

quiet_query = 'SK / 2 >= 0 and SK <= 2'
low_query = 'SK > 2 and SK <= 3'
medium_query = 'SK == 4'
storm_query = 'SK > 4 and SK <= 6'
heavy_storm_query = 'SK > 6'

k_index_table = pd.read_csv( './kindex/k-index.txt', delimiter='\s+')
#quite = list(filter(is_quite, k_index_table))
#quite = k_index_table[(k_index_table["SK"] >= 0) & (k_index_table["SK"] <=0)]
K_DATA ={}

#dates = date.strptime(quiet[0]['DA-MON-YR'][0], '%d-%m-%y')


q_q = ''

for i in range(1,9): 
    and_op = "and" if i<8 else ""
    q_q += f"0 <= `{i}` <= 2 {and_op} "

l_q = '('

for i in range(1,9): 
    and_op = "and" if i<8 else ""
    l_q += f"(0 <= `{i}` <= 3) {and_op} "

l_q += ") and ("


for i in range(1,9):
    or_op = "or" if i<8 else ")"
    l_q += f"`{i}` == 3 {or_op} "


m_q = '('

for i in range(1,9): 
    and_op = "and" if i<8 else ""
    m_q += f"(0 <= `{i}` <= 4) {and_op} "

m_q += ") and ("


for i in range(1,9):
    or_op = "or" if i<8 else ")"
    m_q += f"`{i}` == 4 {or_op} "

    ##
st_q = '('

for i in range(1,9): 
    and_op = "and" if i<8 else ""
    st_q += f"(0 <= `{i}` <= 5) {and_op} "

st_q += ") and ("


for i in range(1,9):
    or_op = "or" if i<8 else ")"
    st_q += f"(5 <= `{i}` <= 6) {or_op} "

h_st_q = '('

for i in range(1,9):
    or_op = "or" if i<8 else ")"
    h_st_q += f"(7 <= `{i}`) {or_op} "

k_index_table["DA-MON-YR"] = pd.to_datetime(k_index_table["DA-MON-YR"], format="%d-%b-%y")

K_DATA["quiet"] = k_index_table.query(q_q)
K_DATA["low"] = k_index_table.query(l_q)
K_DATA["medium"] = k_index_table.query(m_q)
K_DATA["storm"] = k_index_table.query(st_q)
K_DATA["heavy_storm"] = k_index_table.query(h_st_q)

str_dates = {}

for d in K_DATA.keys(): str_dates[d] = K_DATA[d]["DA-MON-YR"].values

dates = {}


for d in str_dates.keys():
    dates[d] = [*str_dates[d]]
