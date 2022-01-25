import pandas as pd
import os


def gs2csv(url, path, fname):
    url_1 = url.replace('/edit#gid=','/export?format=csv&gid=')
    df = pd.read_csv(url_1)
    df.to_csv(os.path.join(path,fname), index=False)

path = '/Users/mistral/Documents/ETHZ/Science/PROGRESS/data'
#studies
fname = '01_studies.csv'
url = "https://docs.google.com/spreadsheets/d/1zxn_8nitemCcFP5D-pGMRHwt6UYowfWnPx_Mq3gXVo4/edit#gid=0"
gs2csv(url, path, fname)

#measurement_info
fname = '02_measurement_info.csv'
url = "https://docs.google.com/spreadsheets/d/1cMvpKicY3UOhsjdb4Y5eAh6GPPy448gLVvYGLEHsUKQ/edit#gid=0"
gs2csv(url, path, fname)

#03_temperatures
fname = '03_temperatures.csv'
url =  "https://docs.google.com/spreadsheets/d/1eB7Al8YUfPR3EYg2ETKw4QKbDFvdGy8W08daHsb94yg/edit#gid=0"
gs2csv(url, path, fname)
