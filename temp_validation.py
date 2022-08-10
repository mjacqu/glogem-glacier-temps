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

for r in regions:
    try:
        reg_id = ggthelp.get_region_id(r, region_lut)


        #figure out which glacier is being used
        files = os.listdir(os.path.join(datapath, r))
        pointfiles = [f for f in files if re.match(r"temp_P\d{1}_\d{5}.dat", f)]

        for pf in pointfiles:
        #pf = pointfiles[0]
            id = re.findall(r"\d{5}", pf)
            rgi_id = ggthelp.full_rgiid(id[0], reg_id)

            #read data from Matthias' output:
            depth = list([1,2,3,4,5,6,7,8,9,14,19,24,29,34,39,44,49,54,59,79,99,119,139,159,179,199,219,239,259, 299]) #added 299 to make enough header lines
            header_pt = ['Year', 'Month'] + depth

            pt, metadata = ggthelp.read_depth_temps(os.path.join(datapath,f"{r}/{pf}"), header_pt, 1)
            model_elevation = float(re.findall(r"\d{3,4}", metadata)[0])
            pt = ggthelp.format_df(pt)

            #read data from validation data
            database_path ='/Users/mistral/git_repos/GloGlaT'
            sites_temps, sites = ggthelp.import_database(database_path)

            #plot measured vs. modeled for all validation sites:
            path = '/Users/mistral/Documents/ETHZ/Science/PROGRESS/data'
            validation_sites = pd.read_csv(os.path.join(path, "initial_test_glaciers.csv"),
                usecols=['rgi_id', 'elevation_masl'])
            validation_data = pd.merge(validation_sites, sites_temps, on=['rgi_id', 'elevation_masl'])

            elevation = validation_data[validation_data.rgi_id==rgi_id].elevation_masl.unique()
            closest_elevation = min(elevation, key=lambda x:abs(x-model_elevation))
            #years = set([d.year for d in validation_data[validation_data.rgi_id==rgi_id].date])
            measured = validation_data[(validation_data["rgi_id"]==rgi_id) & (validation_data["elevation_masl"]==closest_elevation)]
            #calcualte year for model run from
            model_time = measured.start_date + (measured.end_date - measured.start_date)/2
            measured=measured.assign(model_time = model_time)
            years = list(set([d.year for d in measured.model_time]))
            year = [x for x in years if math.isnan(x)==False]

            #What to compare against? The mean of a given year?
            if year == [] or year[0]<1980:
                plot_year = '1990'
                print('no modeled data: using 1990')
            else:
                plot_year = str(year[0])

            depth, model_mean = pt.columns, list(pt.loc[plot_year].mean())

            #1. find overlapping subsets in modeled and measured dataframes

            model_lb, model_ub, meas_lb, meas_ub = ggthelp.get_overlapping_data(measured[measured.model_time==model_time], depth, model_mean)
            validation_depth = depth[model_lb:model_ub]
            validation_temp = model_mean[model_lb:model_ub]
            validation_measured = measured.loc[meas_lb:meas_ub,:]

            interp_temps = []
            for d in validation_measured.depth_m.iteritems():
                lower_idx, upper_idx = ggthelp.get_boundary_idxs(d, validation_depth)
                #print(d[1], depth[lower_idx], depth[upper_idx])
                interp_model_temp = ggthelp.get_model_interpolation(lower_idx, upper_idx, validation_depth, validation_temp, d[1])
                #print(interp_model_temp)
                interp_temps.append(interp_model_temp)

            diffs = interp_temps - validation_measured.temperature_degC
            rmse = np.sqrt(np.sum(diffs**2)/len(diffs))
            mask20 = validation_measured.depth_m>=20
            diffs_20 = diffs[mask20]
            rmse_20 = np.sqrt(np.sum(diffs_20**2)/len(diffs_20))

            #plot
            f, ax = plt.subplots(figsize=(6,9))
            colors = plt.cm.Blues_r(np.linspace(0, 1, 18))
            c_ct = 0
            if year == [] or year[0]<1980:
                plot_year = '1990'
                print('no modeled data: using 1990')
            else:
                plot_year = str(year[0])

            #for i in pt.loc[plot_year].T:
            #    c_ct += 1
            #    ax.plot(pt.loc[i].T, depth,
            #    color=colors[c_ct]
            #)
            ax.scatter(interp_temps, validation_measured.depth_m, color='k', marker='+', label='interpolated points')
            ax.plot(pt.loc[plot_year].mean(), depth, linestyle=':', marker='.', label='model')
            for i in set([m for m in measured.model_time]):
                ax.plot(measured[measured.model_time==i]["temperature_degC"],
                measured[measured.model_time==i]["depth_m"],
                linestyle=':', marker='.',
                label=f"{i} at {closest_elevation} m asl"
            )

            ax.set_xlabel('Temperature (°C)')
            ax.set_ylabel('Depth (m)')
            ax.xaxis.tick_top()
            ax.legend()
            ax.set_title(f"{rgi_id} ({measured.glacier_name.unique()[0]}) \n Model year {plot_year} \n Model elevation: {model_elevation} \n RMSE: {rmse:.2f}, RMSE20: {rmse_20:.2f}")
            f.gca().invert_yaxis()
            f.savefig(f"Val_{r}_{id[0]}.png")

    except ValueError:
        print(f"Glacier {id} in {r} failed, moving on")
