import pandas as pd
import os
from numpy import datetime64

data_column = pd.read_csv( './2017/PET/pet2017dmin.min', delimiter='\s+')
data_column['DATE'] = pd.to_datetime(data_column["DATE"])


def data_by_month(date: str):
    return data_column[data_column['DATE'] == datetime64(date)] 

select_jan = data_column[data_column['DATE'] == datetime64('2017-01-01')]