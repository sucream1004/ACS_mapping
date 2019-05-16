#!/usr/bin/env python
# coding: utf-8
import os
import sys

import numpy as np
import pandas as pd
import geopandas as gpd
import jenkspy

from shapely import wkt

import webbrowser

df = pd.read_json('https://api.census.gov/data/2017/acs/acs5/variables.json')
df = df.reset_index()
print('Loading the variables')

var_names = []
for var,f in zip(df['index'], df['variables']):
    try:
        var_names.append((var, f['label'], f['concept']))
    except:
        continue

var = sys.argv[1]
url = 'https://api.census.gov/data/2017/acs/acs5?get={},NAME&for=tract:*&in=state:36%20county:*'.format(var)
print('Loading {} data'.format(var))
dat = pd.read_json(url)
col_name = [n for n in dat.iloc[0]]
dat.columns = col_name
dat.drop(dat.head(1).index, inplace=True)

dat['cd'] = dat.state + dat.county + dat.tract

for i in range(len(var_names)):
    if sys.argv[1] in var_names[i][0]:
        print(var_names[i])
        ti = var_names[i]

print('Loading census tract data')
ct2010 = pd.read_csv('https://data.cityofnewyork.us/api/views/i69b-3rdj/rows.csv?accessType=api', dtype=str)

ct2010['county'] = None
ct2010['county'][ct2010['BoroName']=='Staten Island'] = '085'
ct2010['county'][ct2010['BoroName']=='Manhattan'] = '061'
ct2010['county'][ct2010['BoroName']=='Brooklyn'] = '047'
ct2010['county'][ct2010['BoroName']=='Bronx'] = '005'
ct2010['county'][ct2010['BoroName']=='Queens'] = '081'

ct2010['cd'] = '36' + ct2010['county'] + ct2010['CT2010']

gdf = gpd.GeoDataFrame(ct2010)
gdf['the_geom'] = gdf['the_geom'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(gdf, geometry='the_geom')
gdf.crs = {'init': 'epsg:4326', 'no_defs': True}
gdf = gdf.merge(dat, on='cd')
gdf.rename(columns = {gdf.columns[14]: 'nb'}, inplace = True)
gdf['nb'] = gdf['nb'].astype(float)
gdf = gdf[gdf['nb'] >= 0]
print('Merging Data')

breaks = jenkspy.jenks_breaks(gdf['nb'], nb_class=5)

import folium
m = folium.Map(location=[40.715005, -73.991396], zoom_start=11, tiles='cartodbpositron')
m.choropleth(geo_data=gdf.to_json(), data=gdf,
             columns=['cd', 'nb'],
             key_on='feature.properties.cd',
             fill_color='Reds',
             bins = breaks #list(gdf['nb'].quantile([0, 0.25, 0.5, 0.75, 1]))
            )
m.save('test.html')
new = 2 # open in a new tab, if possible
url = "file://" + os.getcwd() + "/test.html"
webbrowser.open(url,new=new)
