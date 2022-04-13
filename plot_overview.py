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

datapath ='/Users/mistral/Documents/ETHZ/Science/PROGRESS/data'
studies = pd.read_csv(os.path.join(datapath,'studies.csv'),
    usecols=['study_id', 'first_author', 'year', 'title', 'catalogued'])
sites = pd.read_csv(os.path.join(datapath, 'measurement_info.csv'),
    usecols=['study_id', 'measurement_id', 'location_source', 'y_lat', 'x_lon',
       'epsg', 'elevation_source', 'elevation_masl', 'glacier_name', 'rgi_id',
       'region_range', 'country', 'date', 'to_bottom', 'site_description',
       'notes', 'extraction_method'],
       dtype={'y_lat':np.float64, 'x_lon':np.float64})
temps = pd.read_csv(os.path.join(datapath, 'temperatures.csv'),
    usecols=['study_id', 'measurement_id', 'temperature_degC', 'depth_m'])

#Check equivalence of all id's and indicate where there might be a problem
siteids = list(zip(sites.study_id, sites.measurement_id))
measurementids = list(dict.fromkeys(zip(temps.study_id, temps.measurement_id)))

#testids = [i for i, j in zip(siteids, measurementids) if i != j] #doesn't catch issue if lists are different lengths
testids = set(siteids) - set(measurementids)

if len(testids) > 0:
    print("IDs mismatch: ignoring following entries:")
    print(testids)
    #ignore entries that were found to mismatch before doing join:
    ignoreids = siteids.index(testids.pop())
    sites = sites.drop(index = ignoreids, axis = 0)
else:
    print('IDs match!')


# join sites and temps on study_id and measurement_id keys
sites_temps = pd.merge(sites, temps, on=['study_id', 'measurement_id'])


# for simple plotting, calculate mean of every site
sites['mean_temp'] = sites_temps.groupby(['study_id', 'measurement_id']).temperature_degC.mean().values


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

#1. function to load correct rgi data:
def load_rgi(spatial_data_path, rgi_region):
    '''
    Load rgi shapefile for defined rgi_region (str)
    '''
    filepath = glob.glob(os.path.join(spatial_data_path,f"{rgi_region}_rgi60_*"))[0]
    outlines = gpd.read_file(os.path.join(filepath,f"{os.path.basename(filepath)}.shp"))
    return outlines

#2. function to get all data for plotting based on an rgi-id:
def glacier_data(rgiid, rgi_outlines, sites):
    glacier_outline = rgi_outlines[rgi_outlines.RGIId == rgiid]
    drill_sites = sites[sites.rgi_id == rgiid]
    drill_sites = drill_sites.set_geometry('drill_sites')
    glacier_name = np.unique(drill_sites.glacier_name)[0]
    return glacier_outline, drill_sites, glacier_name

#3. function to create the plot
def glacier_plot(glacier_outline, drill_sites, gn):
    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,6))
    f.suptitle(f"{gn}")
    drill_plot = drill_sites.plot(ax=ax1,
        column='mean_temp',
        cmap='Blues_r',
        vmin=-20, vmax=0,
        markersize=25,
        legend=True,
        legend_kwds={'label':'Mean temperature', 'orientation':'horizontal', 'fraction':0.04, 'pad':0.15},
        edgecolor='k',
        zorder=1
    )
    drill_sites.apply(lambda x: ax1.annotate(
        text=x.measurement_id,
        xy=x.loc['drill_sites'].coords[0],
        xytext=(-5,-10),
        textcoords='offset points',
        fontsize=7),
        axis=1
        )
    glacier_outline.geometry.plot(ax=ax1, edgecolor='black', color='w', zorder=0)
    #
    for i in set(zip(drill_sites.study_id, drill_sites.measurement_id)):
        d = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].depth_m
        t = sites_temps[((sites_temps.study_id==i[0]) & (sites_temps.measurement_id==i[1]))].temperature_degC
        ax2.scatter(t,d, s=3, label=f"{i[1]}", zorder=1)
        ax2.plot(t,d, zorder=0)
        #ax.set_title(f"{drill_sites.measurement_id}")
    ax2.set_ylabel('Depth (m)')
    ax2.set_xlabel('Temperature (Deg. C)')
    ax2.invert_yaxis()
    ax2.legend()
    return(f)




# Now iterate over all regions and save out figure for each glacier

rgi_regions = np.unique([re.findall(r"\-(\d+)\.", id) for id in sites.rgi_id]) #rgi regions from all ids
rgi_files = glob.glob(os.path.join(spatial_data_path, "*rgi60_*")) #all filenames that contain rgi

#Start by iterating over each region, then plot main glacier plot for each unique RGI-ID
for r in rgi_regions:
    #load rgi outlines for one region
    rgi_outlines = load_rgi(spatial_data_path, r)
    #find all rgi_ids from a specific region
    glaciers_in_region = [re.findall(fr"\w+\-{r}\.\d+", id) for id in sites.rgi_id]
    glaciers_in_region = np.unique([x for x in glaciers_in_region if x])
    # now interate over all unique ids in region to pull out corresponding data:
    for id in glaciers_in_region:
        glacier_outline, drill_sites, gn = glacier_data(id, rgi_outlines, sites)
        #then create plot
        f = glacier_plot(glacier_outline, drill_sites, gn)
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
