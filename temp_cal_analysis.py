import numpy as np
import pandas as pd
import GloGlaThelpers as ggthelp
import matplotlib.pyplot as plt
import json
import os
import matplotlib.lines as mlines




# Aggregate all calibration data into one dataset

datapath = '/scratch_net/iceberg_second/mhuss/r6spec_global_results/'
repo_path = '.'
region_lut = pd.read_csv(os.path.join(repo_path,'regionIDs.csv'), dtype=object)
regions = [name for name in os.listdir(datapath) if os.path.isdir(os.path.join(datapath, name))]
sites_temps, sites = ggthelp.import_database(repo_path)
with open('calval.json') as json_file:
    calval = json.load(json_file)

calibration_data = pd.DataFrame()

for r in regions:
    filepath, reg_id = ggthelp.get_file_locations(r, region_lut, datapath)
    try:
        pointfiles = ggthelp.cal_ids_in_region(filepath, r, region_lut, calval)
    except FileNotFoundError:
        print(f"No glaciers in region {r}, moving on")
        continue
    for pf in pointfiles:
        rgi_id, pt_id = ggthelp.get_pointfile_ids(pf, reg_id)
        measured, T_interp, pt, year, model_elevation = ggthelp.build_calval_data(pf, pt_id, reg_id, rgi_id, filepath, sites_temps)
        if len(measured) == 0:
            continue
        measured['T_interp'] = T_interp
        calibration_data = calibration_data.append(measured)

# Scatterplot of all calibration glaciers combined
plt.scatter(calibration_data.temperature_degC, calibration_data.T_interp)
plt.plot([-25, -25, 1, 1], [-25, -25, 1, 1], color='k')
plt.xlabel('Measured temperature')
plt.ylabel('Modeled temperature')
plt.ylim([-25,1])
plt.xlim([-25,1])
plt.show()
