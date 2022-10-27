import GloGlaThelpers as ggthelp
import numpy as np

datapath ='/Users/mistral/git_repos/GloGlaT/'
sites_temps, sites = ggthelp.import_database(datapath)

print(f"Number of studies: {len(np.unique(sites.study_id))}")
print(f"Number of glaciers: {len(np.unique(sites.rgi_id))}")
print(f"Number of profiles: {len(np.unique(sites.measurement_id))}")
print(f"Earliest date: {sites.start_date.min()}")
print(f"Most recent date: {sites.end_date.max()}")
print(f"Deepest borehole: {sites_temps.depth_m.max()}")
print(f"Number of boreholes to glacier bed: {len(sites[sites.to_bottom==True])}")
