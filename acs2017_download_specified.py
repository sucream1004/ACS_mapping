#!/usr/bin/env python
# coding: utf-8
import os
import sys

import pandas as pd
import geopandas as gpd
from shapely import wkt

acs_list = [
'B08006_001E',
'B08006_002E',
'B08006_003E',
'B08006_004E',
'B08006_005E',
'B08006_006E',
'B08006_007E',
'B08006_008E',
'B08006_009E',
'B08006_010E',
'B08006_011E',
'B08006_012E',
'B08006_013E',
'B08006_014E',
'B08006_015E',
'B08006_016E',
'B08006_017E'
]

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

for var in acs_list:

    url = 'https://api.census.gov/data/2017/acs/acs5?get={},NAME&for=tract:*&in=state:36%20county:*'.format(var)
    print('Loading {} data'.format(var))
    dat = pd.read_json(url)
    col_name = [n for n in dat.iloc[0]]
    dat.columns = col_name
    dat.drop(dat.head(1).index, inplace=True)

    dat['cd'] = dat.state + dat.county + dat.tract
    gdf_ = gdf.merge(dat, on='cd')
    gdf_.rename(columns = {gdf_.columns[14]: 'nb'}, inplace = True)
    gdf_['nb'] = gdf_['nb'].astype(float)
    gdf_ = gdf_[gdf_['nb'] >= 0]
    print('Downloading Data')
    fname = 'acs_2017_' + var
    gdf_.to_file(driver = 'GeoJSON', filename= fname + '.geojson')
