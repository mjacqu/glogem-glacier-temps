import numpy as np
import pandas as pd
import os
import GloGlaThelpers as ggthelp
import re
import matplotlib.pyplot as plt
import math
import glob
from scipy import interpolate

datapath = '/scratch_net/iceberg_second/mhuss/r6spec_global_results/'
repo_path = '.'
region_lut = pd.read_csv(os.path.join(repo_path,'regionIDs.csv'), dtype=object)
regions = [name for name in os.listdir(datapath) if os.path.isdir(os.path.join(datapath, name))]
sites_temps, sites = ggthelp.import_database(repo_path)

for r in regions:
    try:
        reg_id = ggthelp.get_region_id(r, region_lut)
        print(f"Running region {r}")
        #for the given region, find the temps simulated at the boreholes
        subdir ='PAST/firnice_temperature/'
        filepath = os.path.join(os.path.join(datapath,r), subdir)
        files = os.listdir(filepath)
    except FileNotFoundError:
        print(f"No glaciers in region {r}, moving on")
        continue

    pointfiles = [f for f in files if re.match(r"temp_ID\d+_\d{5}.dat", f)]

    for pf in pointfiles:
    #pf = pointfiles[0]
        id = re.findall(r"\d{5}", pf)
        rgi_id = ggthelp.full_rgiid(id[0], reg_id)

        #read data from Matthias' output:
        depth = list([1,2,3,4,5,6,7,8,9,14,19,24,29,34,39,44,49,54,59,79,99,119,139,159,179,199,219,239,259, 299]) #added 299 to make enough header lines
        header_pt = ['Year', 'Month'] + depth

        pt, metadata = ggthelp.read_depth_temps(os.path.join(filepath,f"{pf}"), header_pt, 1)
        model_elevation = float(re.findall(r"\d+", metadata)[0])
        pt = ggthelp.format_df(pt)
        pt_id = int(re.search(r"_ID(\d+)_", pf).group(1))

        measured = sites_temps[sites_temps.measurement_id == pt_id]
        if len(measured) == 0:
            continue

        #calcualte year for model run from
        model_time = measured.start_date + (measured.end_date - measured.start_date)/2
        measured=measured.assign(model_time = model_time)
        years = list(set([d.year for d in measured.model_time]))
        year = [x for x in years if math.isnan(x)==False]

        #What to compare against? The mean of a given year?
        if year == [] or year[0]<1980:
            plot_year = '1990'
            print(f"BH #{pt_id} no modeled data: using 1990")
        else:
            plot_year = str(year[0])
            print(f"BH # {pt_id} in year {plot_year}")

        depth, model_mean = pt.columns, list(pt.loc[plot_year].mean())

        f = interpolate.interp1d(depth, model_mean, bounds_error=False)

        T_interp = f(measured.depth_m)
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
        #plot
        f, ax = plt.subplots(figsize=(6,9))
        colors = plt.cm.Blues_r(np.linspace(0, 1, 18))
        c_ct = 0
        if year == [] or year[0]<1980:
            plot_year = '1990'
        else:
            plot_year = str(year[0])

        ax.scatter(T_interp, measured.depth_m, color='k', marker='+', label='interpolated points')
        ax.plot(pt.loc[plot_year].mean(), depth,
            linestyle=':', marker='.',
            label=f"model BH{pt_id}"
        )
        ax.plot(measured.temperature_degC, measured.depth_m,
            linestyle=':', marker='.',
            label=f"measured at BH {measured.measurement_id.unique()[0]}"
        )


        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Depth (m)')
        ax.xaxis.tick_top()
        ax.legend()
        ax.set_title(f"{rgi_id} ({measured.glacier_name.unique()[0]} borehole #{pt_id}) \n Model year {plot_year} \n Model elevation: {model_elevation} \n RMSE: {rmse:.2f}, RMSE20: {rmse_20:.2f}")
        f.gca().invert_yaxis()
        f.savefig(f"{pt_id}_validation.png")
        plt.close(f)
