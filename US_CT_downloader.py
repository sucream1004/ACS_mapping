import os
import sys

import gdown

import pandas as pd
import geopandas as gpd

from functools import reduce

api_key = sys.argv[1]

if len(api_key) < 30:
    sys.exit("It seems that you didn't add API Key.")

def acs():
    url = 'https://drive.google.com/uc?id='
    ids = ['1bkDJxLwIxEJ3YIPepwZDGEjam1xJ-5Ed', '1-dIsrlUQpxpUnwWepUY9imcpDZM6hq3r', '1Gp9BRArCdgnU7CpMahXhc3wX-dbE4CkN', '1MooK_2DDrgSr3oecSkCMezdnTA04-A3k', '1Qh1QEeQVdGZH82ElwoVw_nypOx-X8Yhx']

    if os.path.isfile('census_tract_us.shp'):
        print ("File already exist")
    else:
        print ("Downloading Census Tract TIGER 2019 (Source: https://www2.census.gov/geo/tiger/TIGER2019/)")
        for id_ in ids:
            gdown.download(url + id_)
    var = []

    if len(sys.argv)>=2:
        n = len(sys.argv)
        for i in range(2, n): 
            var.append(sys.argv[i])
        print('Download variable {}'.format(var))
        
    nb = ["%.2d" % i for i in range(100)]
    # var = ['B01001_001E', 'B06011_001E', 'B01002_001E']
    dfs = [[] for i in range(len(var))]
    for i,v in enumerate(var):
        for n in nb:
            try:
                print('Merging variable: {}, state code: {}'.format(v,n), end='\r')
                df = pd.read_json('https://api.census.gov/data/2018/acs/acs5?get={}&for=tract:*&in=state:{}&key={}'.format(v, n, api_key))
                df.columns = df.iloc[0]
                df = df[1:]
                df['GEOID'] = df['state'] + df['county'] + df['tract']
                df = df.drop(['state', 'county', 'tract'], axis=1)
                df[v] = df[v].astype(float)
                dfs[i].append(df)
            except:
                pass

    print('\n Concatenating Dataframes')
    dfs = [pd.concat(d) for d in dfs]
    df = reduce(lambda left,right: pd.merge(left,right,on='GEOID'), dfs)
    return df

df = acs()

def mrg():
    gdf = gpd.read_file('census_tract_us.shp')
    gdf = gdf.merge(df)
    return gdf
gdf = mrg()
gdf.to_file('Census_tract_merged.shp')
print('Complete!')