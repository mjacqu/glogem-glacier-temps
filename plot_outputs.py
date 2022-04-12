import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_depth_temps(fn, header, skp_rows):
    temps = pd.read_table(fn,
        header=skp_rows,
        sep='\s+',
        names=header,
        index_col=None,
        na_values=-99-0
)
    return temps


years = list(np.arange(1980, 2020, 1))
header_gl = years.copy()
header_gl.insert(0,'Elev')

temps_1m = read_depth_temps('firnice_temperature/temp_1m_01450.dat', header_gl, 0)
temps_10m = read_depth_temps('firnice_temperature/temp_10m_01450.dat', header_gl, 0)
temps_50m = read_depth_temps('firnice_temperature/temp_50m_01450.dat', header_gl, 0)
temps_bed = read_depth_temps('firnice_temperature/temp_bedrock_01450.dat', header_gl, 0)

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

dfs = [temps_1m, temps_10m, temps_50m, temps_bed]

flt_1980 = flowline_temperatures(dfs, 1980)
flt_2019 = flowline_temperatures(dfs, 2019)

# depth-dependent temperature along the flowline
h_f = 400
extent = [temps_1m.Elev.values[-1], temps_1m.Elev.values[0],0, h_f]
ticks = [0+h_f/8, 0.25*h_f+h_f/8, 0.5*h_f+h_f/8, 0.75*h_f+h_f/8 ]
ticklabels = ['bed', '50m', '10m', '1m']

f, ax = plt.subplots(figsize = (8,2))
T = ax.imshow(np.fliplr(flt_1980), extent=extent)
ax.set_xlabel('Glacier surface elevation (m asl)')
ax.set_ylabel('Depth')
ax.set_title('Aletsch 1980')
f.gca().set_yticks(ticks)
f.gca().set_yticklabels(ticklabels)
f.colorbar(T)
#f.show()
f.savefig('aletsch_flt_1980.png')

#Evolution of flowline temperatures
h_f = 400
extent = [temps_1m.Elev.values[-1], temps_1m.Elev.values[0],0, h_f]
ticks = [0+h_f/8, 0.25*h_f+h_f/8, 0.5*h_f+h_f/8, 0.75*h_f+h_f/8 ]
ticklabels = ['bed', '50m', '10m', '1m']

f, ax = plt.subplots(figsize = (8,2))
T = ax.imshow(np.fliplr(flt_2019-flt_1980), extent=extent, cmap='Reds')
ax.set_xlabel('Glacier surface elevation (m asl)')
ax.set_ylabel('Depth')
ax.set_title('Aletsch 2019-1980')
f.gca().set_yticks(ticks)
f.gca().set_yticklabels(ticklabels)
f.colorbar(T)
#f.show()
f.savefig('Aletsch_fltdiff_2019-1980.png')



depth = list([1,2,3,4,5,6,7,8,9,14,19,24,29,34,39,44,49,54,59,79,99,119,139,159,179,199,219,239,259,299]) #added 299 to make enough header lines
header_pt = ['Year', 'Month'] + depth

pt1 = read_depth_temps('firnice_temperature/temp_P1_01450.dat', header_pt, 1)
pt2 = read_depth_temps('firnice_temperature/temp_P2_01450.dat', header_pt, 1)
pt3 = read_depth_temps('firnice_temperature/temp_P3_01450.dat', header_pt, 1)

def format_df(df):
    df['Datetime'] = pd.to_datetime({'year':df.Year, 'month':df.Month, 'day':'01'})
    df = df.drop(columns=['Year', 'Month'])
    df = df.set_index('Datetime')
    return df

pt1 = format_df(pt1)
pt2 = format_df(pt2)
pt3 = format_df(pt3)

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
f.savefig('Aletsch_pt1_2000.png')
