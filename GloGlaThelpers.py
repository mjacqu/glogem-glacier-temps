import numpy as np
import pandas as pd
import geopandas as gpd
import os
import glob
import matplotlib.pyplot as plt


#read data from digizied database:
def import_database(path):
    """
    Read digitized data and join studies, measurement metadata and temperatures
    into one database that can be used for plotting.

    Parameters:
    path (str): path to directory that holds stuides.csv, measurement_info.csv,
    temperatures.csv

    Return:
    joined database as pandas dataframe
    """
    studies = pd.read_csv(os.path.join(path,'studies.csv'),
        usecols=['study_id', 'first_author', 'year', 'title', 'included', 'url'])
    sites = pd.read_csv(os.path.join(path, 'measurement_info.csv'),
        usecols=['study_id', 'measurement_id', 'location_source', 'y_lat', 'x_lon',
           'epsg', 'elevation_source', 'elevation_masl', 'glacier_name', 'rgi_id',
            'start_date', 'end_date', 'published_accuracy', 'to_bottom', 'site_description',
           'notes', 'extraction_method'],
           dtype={'y_lat':np.float64, 'x_lon':np.float64})
    temps = pd.read_csv(os.path.join(path, 'data.csv'),
        usecols=['study_id', 'measurement_id', 'temperature_degC', 'depth_m'])
    #Check equivalence of all id's and indicate where there might be a problem
    siteids = list(zip(sites.study_id, sites.measurement_id))
    measurementids = list(dict.fromkeys(zip(temps.study_id, temps.measurement_id)))
    #testids = [i for i, j in zip(siteids, measurementids) if i != j] #doesn't catch issue if lists are different lengths
    testids = list(set(siteids) - set(measurementids))
    print("Check whether all tables list same IDs, drop ones that are not in all tables")
    if len(testids) > 0:
        print("IDs mismatch: ignoring following entries:")
        print(testids)
        #ignore entries that were found to mismatch in sites:
        ignoreids = [siteids.index(p) for p in testids]
        sites = sites.drop(index = ignoreids, axis = 0)
    else:
        print('IDs match!')
    # join sites and temps on study_id and measurement_id keys
    sites_temps = pd.merge(sites, temps, on=['study_id', 'measurement_id'], how='inner').reset_index()
    sites_temps.start_date = pd.to_datetime(sites_temps.start_date)
    sites_temps.end_date = pd.to_datetime(sites_temps.end_date)
    sites.start_date = pd.to_datetime(sites.start_date)
    sites.end_date = pd.to_datetime(sites.end_date)
    return sites_temps, sites

def read_depth_temps(fn, header, skp_rows):
    """
    Read GLOGEM outputs into pandas dataframe
    """
    temps = pd.read_table(fn,
        header=skp_rows,
        sep='\s+',
        names=header,
        index_col=None,
        na_values=-99-0
    )
    with open(fn) as f:
        header_info = next(f)
    return temps, header_info

#plot temperatures along glacier for one year
def flowline_temperatures(dfs, year):
    '''
    dfs (list): list of arrays to be used
    year (int): year for which to compile flowline temperatures
    '''
    flt = np.vstack((dfs[0][year].T,
        dfs[1][year].T,
        dfs[2][year].T,
        dfs[3][year].T)
    )
    return flt

#1. function to load correct rgi data:
def load_rgi(spatial_data_path, rgi_region):
    '''
    Load rgi shapefile for defined rgi_region (str)
    '''
    filepath = glob.glob(os.path.join(spatial_data_path,f"{rgi_region}_rgi60_*"))[0]
    outlines = gpd.read_file(os.path.join(filepath,f"{os.path.basename(filepath)}.shp"))
    return outlines

# Format dataframe with point data
def format_df(df):
    df['Datetime'] = pd.to_datetime({'year':df.Year, 'month':df.Month, 'day':'01'})
    df = df.drop(columns=['Year', 'Month'])
    df = df.set_index('Datetime')
    return df


#2. function to get all data for plotting based on an rgi-id:
def glacier_data(rgiid, rgi_outlines, sites):
    glacier_outline = rgi_outlines[rgi_outlines.RGIId == rgiid]
    drill_sites = sites[sites.rgi_id == rgiid]
    drill_sites = drill_sites.set_geometry('drill_sites')
    glacier_name = np.unique(drill_sites.glacier_name)[0]
    return glacier_outline, drill_sites, glacier_name

#3. function to create the plot
def glacier_plot(sites_temps, glacier_outline, drill_sites, gn):
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

#get glacier name from rgi id
def full_rgiid(rgiid, region_id):
    """
    return the full rgiid from region and rgi_id
    """
    full_id = f"RGI60-{region_id}.{rgiid}"
    return full_id

# get region-id from look up table
def get_region_id(region_name, lut):
    """
    get region id from look up table of region names and IDs
    """
    return lut[lut['region-name']==region_name]['rgi-reg'].iat[0]
