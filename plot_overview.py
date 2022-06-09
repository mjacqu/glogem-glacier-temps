import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import difflib
import math
import glob
from pyproj import Proj, transform
from shapely.geometry import Point
import re
import GloGlaThelpers as ggthelp


plt.plot()
plt.show()

#import world map
world = gpd.read_file('/Users/mistral/Documents/CUBoulder/Science/spatial_base_data/world.geo.json')

#import global glaciers
rgipath = '/Users/mistral/Documents/CUBoulder/Science/spatial_base_data/buffered_glacier_outlines'
rgi = gpd.read_file(os.path.join(rgipath, 'rgi60_buff_diss.shp'))

#import all attributes from rgi (including center lat/long)
spatial_data_path = '/Users/mistral/Documents/CUBoulder/Science/spatial_base_data'
rgi_attribs = pd.concat(
    [pd.read_csv(f, encoding='latin1') for f in glob.glob(os.path.join(spatial_data_path,'00_rgi60_attribs/*.csv'))],
    ignore_index = True
)

#load and construct database
datapath ='/Users/mistral/git_repos/GloGlaT/'
sites_temps, sites = ggthelp.import_database(datapath)

# for simple plotting, calculate mean of every site
sites['mean_temp'] = sites_temps.groupby(['measurement_id']).temperature_degC.mean().values

# add corresponding center_lat/long to sites from rgi_pts
rgi_attribs_gdf = gpd.GeoDataFrame(rgi_attribs, geometry=gpd.points_from_xy(rgi_attribs.CenLon,rgi_attribs.CenLat))
sites['glacier_centerpt'] = pd.DataFrame([rgi_attribs_gdf[rgi_attribs_gdf['RGIId']==g].geometry.values for g in sites['rgi_id']]) #get rgi centerpoint coordinates for each entry


#add geometry of measurement site
drill_site = []
outProj = Proj('epsg:4326')
for code,coords in zip(sites.epsg.iteritems(), (zip(sites.x_lon, sites.y_lat))):
    if ~np.isnan(code[1]):
        #print(code[1])
        inProj = Proj('epsg:'+str(int(code[1])))
        ds = transform(inProj,outProj,coords[0], coords[1]) #check UTM coords --> wrong transformation
        ds = (ds[1], ds[0])
        drill_site.append(ds)
    else:
        drill_site.append(coords)

sites['drill_sites'] = gpd.GeoSeries([Point(coord[0], coord[1]) for coord in drill_site])

sites = gpd.GeoDataFrame(sites)
#create colormap

#sites = sites.set_geometry('drill_sites')
sites = sites.set_geometry('glacier_centerpt')
#plot overview map
f, ax = plt.subplots(figsize=(12,6))
world.plot(ax=ax, color='white', edgecolor='silver', zorder=1)
rgi.geometry.plot(ax=ax, color='cyan')
t_plot = sites.plot(ax=ax,
    column='mean_temp',
    cmap='Blues_r',
    vmin=-20, vmax=0,
    markersize=25,
    legend=True,
    legend_kwds={'label':'Temperature', 'orientation':'horizontal', 'fraction':0.04, 'pad':0.15},
    edgecolor='k'
)
ax.set_ylim([-60,90])
ax.set_xlim([-180,180])
f.tight_layout()
f.savefig("/Users/mistral/Documents/ETHZ/Science/PROGRESS/outputs/thermal_regimes.pdf")
#f.savefig('thermal_regimes.pdf')

#Plot boreholes sites on individual glaciers
# Now iterate over all regions and save out figure for each glacier

rgi_regions = np.unique([re.findall(r"\-(\d+)\.", id) for id in sites.rgi_id]) #rgi regions from all ids
rgi_files = glob.glob(os.path.join(spatial_data_path, "*rgi60_*")) #all filenames that contain rgi

#Start by iterating over each region, then plot main glacier plot for each unique RGI-ID
for r in rgi_regions:
    #load rgi outlines for one region
    rgi_outlines = ggthelp.load_rgi(spatial_data_path, r)
    #find all rgi_ids from a specific region
    glaciers_in_region = [re.findall(fr"\w+\-{r}\.\d+", id) for id in sites.rgi_id]
    glaciers_in_region = np.unique([x for x in glaciers_in_region if x])
    # now interate over all unique ids in region to pull out corresponding data:
    for id in glaciers_in_region:
        glacier_outline, drill_sites, gn = ggthelp.glacier_data(id, rgi_outlines, sites)
        #then create plot
        f = ggthelp.glacier_plot(glacier_outline, drill_sites, gn)
        f.savefig(f"/Users/mistral/Documents/ETHZ/Science/PROGRESS/outputs/all_glaciers/{gn}.pdf")
        f.close()
'''
#plot individual measurement site (one plot per borehole)
for i in set(zip(drill_sites.study_id, drill_sites.measurement_id)):
    d = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].depth_m
    t = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].temperature_degC
    title = np.unique(sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].glacier_name)[0]
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
        f.show()
        #f.savefig(f"{title}-{i[1]}.png")

    #next: add subplot with profile for each borehole
    nr_plots = len(set(zip(drill_sites.study_id, drill_sites.measurement_id)))
    Cols = int(nr_plots**0.5)
    Rows = np.ceil(nr_plots/Cols)

    Position = range(1,nr_plots + 1)

    fig = plt.figure(1, figsize = (8,10))
    k=0
    for i in set(zip(drill_sites.study_id, drill_sites.measurement_id)):
        fig.gca().invert_yaxis()
        # add every single subplot to the figure with a for loo
        d = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].depth_m
        t = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].temperature_degC
        ax = fig.add_subplot(int(Rows),int(Cols),Position[k])
        ax.scatter(t,d, s=2, c='r')
        ax.plot(t,d, linewidth=0.5, c='k')     # Or whatever you want in the subplot
        k+=1

    plt.show()

'''
