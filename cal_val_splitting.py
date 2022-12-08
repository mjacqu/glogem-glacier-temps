import numpy as np
import pandas as pd
import re
import random
import json

#Goal: list of indicies that keeps roughly 50% of ids in each region
data = pd.read_csv('input_glogem.csv')
rgi_list = pd.read_csv('regionIDs.csv')

data['region'] = data.rgi_id.str.extract(r"RGI60-(\d+).").astype(int)
data = data.merge(rgi_list, how='inner', left_on='region', right_on='rgi-reg')

cal_val = []

for r in rgi_list['rgi-reg']:
    reg_subset = data[data.region==r].measurement_id
    region_name = data['region-name'][data.region==r].unique()
    n = np.ceil(len(reg_subset)/2)
    if n==0:
        continue
    cal = random.sample(list(reg_subset), int(n))
    val = list(set(reg_subset).difference(list(cal)))
    dict = {'region': region_name[0], 'cal_val': [{'cal': cal}, {'val': val}]}
    cal_val.append(dict)

# uncomment in case new version is needed
#with open('calval.json', 'w') as f:
#    json.dump(cal_val, f, indent=2)
