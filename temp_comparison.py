import numpy as np
import pandas as pd
import os
import GloGlaThelpers as ggthelp
import re
import matplotlib.pyplot as plt
import math
import glob

#plt.plot()
#plt.show()

datapath = '/Users/mistral/Documents/ETHZ/Science/PROGRESS/data/firnice_temperature'
region_lut = pd.read_csv(os.path.join(datapath,'regionIDs.csv'), dtype=object)
regions = [name for name in os.listdir(datapath) if os.path.isdir(os.path.join(datapath, name))]

#test with one dataset
region_name = 'SouthAsiaEast'
reg_id = ggthelp.get_region_id(region_name, region_lut)


#figure out which glacier is being used
files = os.listdir(os.path.join(datapath, region_name))
pointfiles = [f for f in files if re.match(r"temp_P\d{1}_\d{5}.dat", f)]

for pf in pointfiles:
    id = re.findall(r"\d{5}", pf)
    rgi_id = ggthelp.full_rgiid(id[0], reg_id)

    #read data from Matthias' output:
    depth = list([1,2,3,4,5,6,7,8,9,14,19,24,29,34,39,44,49,54,59,79,99,119,139,159,179,199,219,239,259, 299]) #added 299 to make enough header lines
    header_pt = ['Year', 'Month'] + depth

    pt, metadata = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/{pf}"), header_pt, 1)
    model_elevation = float(re.findall(r"\d{3,4}", metadata)[0])
    pt = ggthelp.format_df(pt)


    #read data from validation data
    database_path ='/Users/mistral/git_repos/GloGlaT'
    sites_temps = ggthelp.import_database(database_path)

    #plot measured vs. modeled for all validation sites:
    path = '/Users/mistral/Documents/ETHZ/Science/PROGRESS/data'
    validation_sites = pd.read_csv(os.path.join(path, "initial_test_glaciers.csv"),
        usecols=['rgi_id', 'elevation_masl'])
    validation_data = pd.merge(validation_sites, sites_temps, on=['rgi_id', 'elevation_masl'])


    elevation = validation_data[validation_data.rgi_id==rgi_id].elevation_masl.unique()
    closest_elevation = min(elevation, key=lambda x:abs(x-model_elevation))
    #years = set([d.year for d in validation_data[validation_data.rgi_id==rgi_id].date])

    measured = validation_data[(validation_data["rgi_id"]==rgi_id) & (validation_data["elevation_masl"]==closest_elevation)]
    years = list(set([d.year for d in measured.date]))
    year = [x for x in years if math.isnan(x)==False]

    #plot data at point by year
    f, ax = plt.subplots(figsize=(6,8))
    colors = plt.cm.Blues_r(np.linspace(0, 1, 18))
    c_ct = 0
    if year == [] or year[0]<1980:
        plot_year = '1990'
        print('no modeled data: using 1990')
    else:
        plot_year = str(year[0])

    for i in pt.loc[plot_year].T:
        c_ct += 1
        ax.plot(pt.loc[i].T, depth,
        color=colors[c_ct]
    )

    for i in set([m for m in measured.date]):
        ax.plot(measured[measured.date==i]["temperature_degC"],
        measured[measured.date==i]["depth_m"],
        linestyle=':', marker='.',
        label=f"{i} at {closest_elevation} m asl"
    )

    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Depth (m)')
    ax.xaxis.tick_top()
    ax.legend()
    ax.set_title(f"{rgi_id} ({measured.glacier_name.unique()[0]}) \n Model year {plot_year} \n Model elevation: {model_elevation}")
    f.gca().invert_yaxis()
    f.show()
    #f.savefig(f"{rgi_id}.png")
