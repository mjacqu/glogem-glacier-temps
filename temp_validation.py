import numpy as np
import pandas as pd
import os
import GloGlaThelpers as ggthelp
import re
import matplotlib.pyplot as plt
import math
import glob
from scipy import interpolate
import json

datapath = '/scratch_net/iceberg_second/mhuss/r6spec_global_results/'
repo_path = '.'
region_lut = pd.read_csv(os.path.join(repo_path,'regionIDs.csv'), dtype=object)
regions = [name for name in os.listdir(datapath) if os.path.isdir(os.path.join(datapath, name))]
sites_temps, sites = ggthelp.import_database(repo_path)
with open('calval.json') as json_file:
    calval = json.load(json_file)


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

        diffs = T_interp - measured.temperature_degC
        try:
            rmse = np.sqrt(np.sum(diffs**2)/len(diffs))
        except ZeroDivisionError:
            rmse_20 = np.nan
        mask20 = measured.depth_m>=20
        diffs_20 = diffs[mask20]
        try:
            rmse_20 = np.sqrt(np.sum(diffs_20**2)/len(diffs_20))
        except ZeroDivisionError:
            rmse_20 = np.nan

        #lineplot showing measured and modeled data per glacier
        f, ax = plt.subplots(figsize=(6,9))
        colors = plt.cm.Blues_r(np.linspace(0, 1, 18))
        c_ct = 0
        if year == [] or year[0]<1980:
            plot_year = '1990'
        else:
            plot_year = str(year[0])

        ax.scatter(T_interp, measured.depth_m, color='k', marker='+', label='interpolated points')
        ax.plot(pt.loc[plot_year].mean(), pt.columns,
            linestyle=':', marker='.',
            label=f"model BH{pt_id}"
        )
        ax.plot(measured.temperature_degC, measured.depth_m,
            linestyle=':', marker='.',
            label=f"measured at BH {measured.measurement_id.unique()[0]}"
        )

        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Depth (m)')
        #ax1.xaxis.tick_top()
        ax.invert_yaxis()
        ax.legend()
        ax.set_title(f"{rgi_id} ({measured.glacier_name.unique()[0]} borehole #{pt_id}) \n Model year {plot_year} \n Model elevation: {model_elevation} \n RMSE: {rmse:.2f}, RMSE20: {rmse_20:.2f}")

        #ax2.scatter(T_interp, measured.temperature_degC)
        #ax2.set_xlabel('Modeled temperature')
        #ax2.set_ylabel('Measured temperature')
        #ax2.axis('equal')
        #ax2.set_aspect('equal')

        f.savefig(f"Temp_val_outputs/{pt_id}_validation.png")
        plt.close(f)
