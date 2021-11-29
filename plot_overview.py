import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import difflib
import math
import glob

plt.plot()
plt.show()

#import world map
world = gpd.read_file('/Users/mistral/Documents/CUBoulder/Science/spatial_base_data/world.geo.json')

#import global glaciers
rgipath = '/Users/mistral/Documents/CUBoulder/Science/spatial_base_data/buffered_glacier_outlines'
rgi = gpd.read_file(os.path.join(rgipath, 'rgi60_buff_diss.shp'))

#import all attributes from rgi (including center lat/long)
rgi_attribs = pd.concat(
    [pd.read_csv(f, encoding='latin1') for f in glob.glob('/Users/mistral/Documents/CUBoulder/Science/spatial_base_data/00_rgi60_attribs/*.csv')],
    ignore_index = True
)

datapath ='/Users/mistral/Documents/ETHZ/Science/PROGRESS/data'
studies = pd.read_csv(os.path.join(datapath,'01_studies.csv'))
sites = pd.read_csv(os.path.join(datapath, '02_studysites.csv'))
temps = pd.read_csv(os.path.join(datapath, '03_temperatures.csv'))

# join sites and temps on study_id and measurement_id keys
sites_temps = pd.merge(sites, temps, on=['study_id', 'measurement_id'])

# for simple plotting, calculate mean of every site
sites['mean_temp'] = sites_temps.groupby(['study_id', 'measurement_id']).temperature.mean().values

# add corresponding center_lat/long to sites from rgi_pts
rgi_attribs_gdf = gpd.GeoDataFrame(rgi_attribs, geometry=gpd.points_from_xy(rgi_attribs.CenLon,rgi_attribs.CenLat))
sites['geometry'] = pd.DataFrame([rgi_attribs_gdf[rgi_attribs_gdf['RGIId']==g].geometry.values for g in sites['rgi_id']])
sites = gpd.GeoDataFrame(sites)


#plot overview map
f, ax = plt.subplots(figsize=(9,4))
world.plot(ax=ax, color='white', edgecolor='silver', zorder=1)
rgi.geometry.plot(ax=ax, color='cyan')
t_plot = sites.plot(ax=ax,
    column='mean_temp',
    cmap='Reds',
    vmin=-20, vmax=0,
    markersize=15,
    legend=True,
    legend_kwds={'label':'Temperature', 'orientation':'horizontal', 'fraction':0.04, 'pad':0.15},
    edgecolor='k'
)
ax.set_ylim([-60,90])
ax.set_xlim([-180,180])
f.tight_layout()
f.show()
#f.savefig('thermal_regimes.pdf')

#plot individual measurement site
for i in set(zip(sites_temps.study_id, sites_temps.measurement_id)):
    d = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].depth
    t = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].temperature
    title = np.unique(sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].glacier)[0]
    # plot depth vs. temperature with depth increasing down
    if len(d)>1:
        f, ax = plt.subplots(figsize=(5,5))
        ax.plot(t,d, color='k', linestyle=':', marker='.')
        ax.set_title(f"{title}-{i[1]}")
        ax.xaxis.tick_top()
        ax.set_xlabel('Temperature')
        ax.xaxis.set_label_position('top')
        ax.set_ylabel('Depth (m)')
        f.gca().invert_yaxis()
        #f.show()
        f.savefig(f"{title}-{i[1]}.png")
