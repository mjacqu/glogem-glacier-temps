import numpy as np
import pandas as pd

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
    return temps

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
