import pandas as pd
import numpy as np
import os
import re

datapath = './import_datasets'
fn = 'Thermistor241_RikhaSamba.csv'

data = pd.read_csv(os.path.join(datapath,fn),
    header=0,
    names=['datetime', '0.05', '0.1', '0.3', '0.5', '1', '1.5' , '2', '3', '4', '6', '8', '10'],
    usecols = [0,7,8,9,10,11,12,13,14,15,16,17,18]
)

#depth_labels = data.filter(regex='TK144_[\d]+cm').columns

data = pd.melt(data, id_vars=['datetime'],
    value_vars=data.columns[1:],
    var_name='depth_m',
    value_name='temperature_degC'
).sort_values(['datetime', 'depth_m'])

data['datetime'] = pd.to_datetime(data.datetime, infer_datetime_format=True)

data = data.astype({'depth_m':'float'})
data.loc[data.temperature_degC<-50] = np.nan

daily_means = data.set_index('datetime').groupby([pd.Grouper(freq='D'), 'depth_m']).mean()

fig, ax = plt.subplots(figsize=(8,6))
daily_means.groupby('datetime').plot( ax=ax)

fig, ax = plt.subplots(figsize=(8,6))
for label, df in daily_means.groupby('datetime'):
    df.temperature_degC.plot(ax=ax, color='grey')

#plt.gca().invert_yaxis()
plt.show()
