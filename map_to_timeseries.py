import GloGlaThelpers as ggthelp
import pandas as pd
import numpy as np
import os

datapath ='/Users/mistral/git_repos/GloGlaT/'
sites_temps, sites = ggthelp.import_database(datapath)

measurement_times = sites[['study_id','measurement_id', 'start_date', 'end_date']].copy()
measurement_times['time_id'] = np.arange(1,len(measurement_times)+1)

temps = pd.read_csv(os.path.join(datapath, 'data.csv'),
    usecols=[0,1,2,3]
)

temps = temps.merge(
    measurement_times[['measurement_id', 'time_id']],
    on='measurement_id',
    how='right',
    validate='many_to_one'
)

temps = temps[['study_id', 'measurement_id', 'time_id', 'temperature_degC', 'depth_m']]
measurement_times = measurement_times[['study_id', 'measurement_id', 'time_id', 'start_date', 'end_date']]

temps.to_csv('data_with_tempid.csv')
measurement_times.to_csv('measurement_times.csv')
