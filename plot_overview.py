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
studies = pd.read_csv(os.path.join(datapath,'01_studies.csv'),
    usecols=['study_id', 'title', 'first_author', 'year', 'catalogued'])
sites = pd.read_csv(os.path.join(datapath, '02_measurement_info.csv'),
    usecols=['study_id', 'measurement_id', 'location_source', 'y_lat', 'x_lon',
       'epsg', 'elevation_source', 'elevation_masl', 'glacier_name', 'rgi_id',
       'region_range', 'country', 'date', 'to_bottom', 'site_description',
       'notes', 'extraction_method'],
       dtype={'y_lat':np.float64, 'x_lon':np.float64})
temps = pd.read_csv(os.path.join(datapath, '03_temperatures.csv'),
    usecols=['study_id', 'measurement_id', 'temperature_degC', 'depth_m'])

#Check equivalence of all id's and indicate where there might be a problem
siteids = list(zip(sites.study_id, sites.measurement_id))
measurementids = list(dict.fromkeys(zip(temps.study_id, temps.measurement_id)))

#testids = [i for i, j in zip(siteids, measurementids) if i != j] #doesn't catch issue if lists are different lengths
testids = set(siteids) - set(measurementids)

if len(testids) > 0:
    print("IDs mismatch: ignoring following entries:")
    print(testids)
else:
    print('IDs match!')

#ignore entries that were found to mismatch before doing join:
ignoreids = siteids.index(testids.pop())
sites = sites.drop(index = ignoreids, axis = 0)

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
f.show()
#f.savefig('thermal_regimes.pdf')

#Plot boreholes sites on individual glaciers

rgi_regions = np.unique([re.findall(r"\-(\d+)\.", id) for id in sites.rgi_id]) #rgi regions from all ids
rgi_files = glob.glob(os.path.join(spatial_data_path, "*rgi60_*")) #all filenames that contain rgi

def load_rgi(spatial_data_path, rgi_region):
    '''
    Load rgi shapefile for defined rgi_region (str)
    '''
    filepath = glob.glob(os.path.join(spatial_data_path,f"{rgi_region}_rgi60_*"))[0]
    outlines = gpd.read_file(os.path.join(filepath,f"{os.path.basename(filepath)}.shp"))
    return outlines


region = '03'
rgi_outlines = load_rgi(spatial_data_path, region)

glaciers_in_region = [re.findall(fr"\w+\-{nr}\.\d+", id) for id in sites.rgi_id] #finds all rgi_ids from a specific region
glaciers_in_region = [x for x in glaciers_in_region if x]

def glacier_data(rgiid, rgi_outlines, sites):
    glacier_outline = rgi_outlines[rgi_outlines.RGIId == rgiid]
    drill_sites = sites[sites.rgi_id == rgiid]
    drill_sites = drill_sites.set_geometry('drill_sites')
    glacier_name = np.unique(drill_sites.glacier_name)[0]
    return glacier_outline, drill_sites, glacier_name

rgiid = 'RGI60-03.04539'

glacier_outline, drill_sites, gn = glacier_data(rgiid, rgi_outlines, sites)

f, ax = plt.subplots()
drill_plot = drill_sites.plot(ax=ax,
    column='mean_temp',
    cmap='Blues_r',
    vmin=-20, vmax=0,
    markersize=25,
    legend=True,
    legend_kwds={'label':'Temperature', 'orientation':'horizontal', 'fraction':0.04, 'pad':0.15},
    edgecolor='k',
    zorder=1
)
glacier_outline.geometry.plot(ax=ax, edgecolor='black', color='w', zorder=0)
ax.set_title(f"{gn}")
f.tight_layout()
f.show()

'''
#plot individual measurement site (one plot per borehole)
for i in set(zip(sites_temps.study_id, sites_temps.measurement_id)):
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
'''
