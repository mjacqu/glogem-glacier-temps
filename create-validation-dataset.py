import GloGlaThelpers as ggthelp
import random
import numpy as np
import pickle
import pandas as pd
from pyproj import Proj, transform

#load and construct database
datapath ='/Users/mistral/git_repos/GloGlaT/'
sites_temps, sites = ggthelp.import_database(datapath)

#add maximum depth to sites DataFrame
max_depth = sites_temps.groupby(sites_temps.measurement_id).depth_m.max()
sites = sites.assign(max_depth=max_depth.values)

#calcualte year for model run from
model_time = sites.start_date + (sites.end_date - sites.start_date)/2
sites=sites.assign(model_time = model_time)

#
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

sites = sites.assign(site_coords = drill_site)

sites = sites.drop(columns=['location_source', 'y_lat', 'x_lon', 'epsg', 'elevation_source', 'published_accuracy', 'extraction_method'])

mathias_df = sites.to_csv('input_glogem.csv', index=False)
# Generate list of Id's used for model tuning
# Decided against this: can do the filtering later
