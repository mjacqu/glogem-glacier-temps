import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import GloGlaThelpers as ggthelp
from scipy import interpolate


path = '/Users/mistral/git_repos/GloGlaT'

orig_dig = pd.read_csv(os.path.join(path, 'temperatures.csv'),
    usecols=['study_id', 'measurement_id', 'temperature_degC', 'depth_m'])

re_dig = temps = pd.read_csv(os.path.join(path, 'redigitized_temps.csv'),
    usecols=['study_id', 'measurement_id', 'temperature_degC', 'depth_m'])

check_dig = pd.merge(orig_dig, re_dig, on=['study_id', 'measurement_id'], how='inner')

diffs = []
for i in set(zip(check_dig.study_id, check_dig.measurement_id)):
    try:
        f = interpolate.interp1d(orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].depth_m, orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].temperature_degC, bounds_error=False)
    except ValueError:
        print(f"{i[0]}_{i[1]} doesn't have enough values, skipping")
    T_interp = f(re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].depth_m)
    diff = T_interp - re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].temperature_degC
    diffs.append(diff)



for i in set(zip(check_dig.study_id, check_dig.measurement_id)):
    f, ax = plt.subplots()
    d_orig = orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].depth_m
    t_orig = orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].temperature_degC
    d_redig = re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].depth_m
    t_redig = re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].temperature_degC
    ax.scatter(t_orig, d_orig, label='original digitization')
    ax.scatter(t_redig, d_redig, label='redigitized')
    ax.set_ylabel('Depth (m)')
    ax.set_xlabel('Temperature (Deg. C)')
    ax.invert_yaxis()
    ax.legend()
    f.savefig(f"digitization_assessment/{i[0]}_{i[1]}.png")

plt.close('all')

#Plot histogram of median differences between two digitizations
f, ax = plt.subplots()
ax.hist([d.median() for d in diffs], bins=100)
ax.set_title('Digitization differences')
ax.set_xlabel('Temperature (°C)')
ax.set_ylabel('Number of digitizations')
f.savefig('digitization_assessment/hist_of_diffs.png')

f, ax = plt.subplots()
ax.hist([d.median() for d in diffs], bins=100)
ax.set_title('Digitization differences')
ax.set_xlabel('Temperature (°C)')
ax.set_ylabel('Number of digitizations')
ax.set_xlim([-2,2])
f.savefig('digitization_assessment/zoom_hist_of_diffs.png')


ids = list(set(zip(check_dig.study_id, check_dig.measurement_id)))
i = ids[0]

f = interpolate.interp1d(orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].depth_m, orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].temperature_degC, bounds_error=False)
T_interp = f(re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].depth_m)

diffs = T_interp - re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].temperature_degC
rmse = np.sqrt(np.sum(diffs**2)/len(diffs))

f, ax = plt.subplots()
d_orig = orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].depth_m
t_orig = orig_dig[(orig_dig.study_id==i[0]) & (orig_dig.measurement_id==i[1])].temperature_degC
d_redig = re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].depth_m
t_redig = re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].temperature_degC
ax.scatter(t_orig, d_orig, label='original digitization')
ax.scatter(t_redig, d_redig, label='redigitized')
ax.scatter(T_interp, re_dig[(re_dig.study_id==i[0]) & (re_dig.measurement_id==i[1])].depth_m, color='k', marker='+', label='interpolated points')
ax.set_ylabel('Depth (m)')
ax.set_xlabel('Temperature (Deg. C)')
ax.invert_yaxis()
ax.legend()
f.show()
