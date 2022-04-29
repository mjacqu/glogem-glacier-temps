import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import GloGlaThelpers as ggthelp


years = list(np.arange(1980, 2020, 1))
header_gl = years.copy()
header_gl.insert(0,'Elev')

datapath = '/Users/mistral/Documents/ETHZ/Science/PROGRESS/data/firnice_temperature'
region_name = 'CentralEurope'
rgiid = '01450'
regionlist = pd.read_csv(os.path.join(datapath,'regionIDs.csv'))
region_id = ggthelp.get_region_id(region_name, regionlist)

glacier_id = ggthelp.full_rgiid(rgiid, region_id)

temps_1m = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/temp_1m_{rgiid}.dat"), header_gl, 0)
temps_10m = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/temp_10m_{rgiid}.dat"), header_gl, 0)
temps_50m = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/temp_50m_{rgiid}.dat"), header_gl, 0)
temps_bed = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/temp_bedrock_{rgiid}.dat"), header_gl, 0)


dfs = [temps_1m, temps_10m, temps_50m, temps_bed]

flt_1980 = ggthelp.flowline_temperatures(dfs, 1990)
flt_2019 = ggthelp.flowline_temperatures(dfs, 2019)

# depth-dependent temperature along the flowline
h_f = 400
extent = [temps_1m.Elev.values[-1], temps_1m.Elev.values[0],0, h_f]
ticks = [0+h_f/8, 0.25*h_f+h_f/8, 0.5*h_f+h_f/8, 0.75*h_f+h_f/8 ]
ticklabels = ['bed', '50m', '10m', '1m']

f, ax = plt.subplots(figsize = (8,2))
T = ax.imshow(np.fliplr(flt_2019), extent=extent)
ax.set_xlabel('Glacier surface elevation (m asl)')
ax.set_ylabel('Depth')
ax.set_title(f"{glacier_id}")
f.gca().set_yticks(ticks)
f.gca().set_yticklabels(ticklabels)
f.colorbar(T)
f.show()
#f.savefig('aletsch_flt_1980.png')

#Evolution of flowline temperatures
h_f = 400
extent = [temps_1m.Elev.values[-1], temps_1m.Elev.values[0],0, h_f]
ticks = [0+h_f/8, 0.25*h_f+h_f/8, 0.5*h_f+h_f/8, 0.75*h_f+h_f/8 ]
ticklabels = ['bed', '50m', '10m', '1m']

f, ax = plt.subplots(figsize = (8,2))
T = ax.imshow(np.fliplr(flt_2019-flt_1980), extent=extent, cmap='Reds')
ax.set_xlabel('Glacier surface elevation (m asl)')
ax.set_ylabel('Depth')
ax.set_title(f"{glacier_id}")
f.gca().set_yticks(ticks)
f.gca().set_yticklabels(ticklabels)
f.colorbar(T)
f.show()
#f.savefig('Aletsch_fltdiff_2019-1980.png')



depth = list([1,2,3,4,5,6,7,8,9,14,19,24,29,34,39,44,49,54,59,79,99,119,139,159,179,199,219,239,259, 299]) #added 299 to make enough header lines
header_pt = ['Year', 'Month'] + depth

pt1 = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/temp_P1_{rgiid}.dat"), header_pt, 1)
pt2 = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/temp_P2_{rgiid}.dat"), header_pt, 1)
pt3 = ggthelp.read_depth_temps(os.path.join(datapath,f"{region_name}/temp_P3_{rgiid}.dat"), header_pt, 1)

pt1 = ggthelp.format_df(pt1)
pt2 = ggthelp.format_df(pt2)
pt3 = ggthelp.format_df(pt3)

#plot data at point by year
f, ax = plt.subplots()
colors = plt.cm.Blues_r(np.linspace(0, 1, 18))
c_ct = 0
for i in pt1.loc['2000'].T:
    c_ct += 1
    ax.plot(pt1.loc[i].T, depth,
    color=colors[c_ct]
    )

ax.set_xlabel('Temperature (°C)')
ax.set_ylabel('Depth (m)')
ax.xaxis.tick_top()
ax.set_title('Aletsch Pt. 1 (2095 m asl)')
f.gca().invert_yaxis()
f.show()
#f.savefig('Aletsch_pt1_2000.png')
