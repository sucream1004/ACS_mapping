import os

import jenkspy
import numpy as np
import pandas as pd
import geopandas as gpd

from shapely import wkt

import folium
import webbrowser
from glob import glob

f_ = glob('*.geojson')
gdf = []
for f in f_:
    gdf.append(gpd.read_file(f))

breaks = []
for gdf_ in gdf:
    breaks.append(jenkspy.jenks_breaks(gdf_['nb'], nb_class=5))

from branca.element import MacroElement
from branca import colormap

from jinja2 import Template

class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)

legend = ['Total',
          'Car truck or van',
          'Car truck or van!!Drove alone',
          'Car truck or van!!Carpooled',
          'Car truck or van!!Carpooled!!2-person',
          'Car truck or van!!Carpooled!!3-person',
          'Car truck or van!!Carpooled!!4-or-more',
          'Public Transportation',
          'Public Transportation!!Bus or trolley bus',
          'Public Transportation!!Streetscar or trolley car',
          'Public Transportation!!Subway or elevated',
          'Public Transportation!!Railroad',
          'Public Transportation!!Ferryboat',
          'Bicycle',
          'Walked',
          'Taxicab motorcycle or other means',
          'Worked at home'
          ]
m = folium.Map(location=[40.715005, -73.991396],
               zoom_start=11, tiles='cartodbpositron')

color_code = ['#FCEBE3', '#FBC4AE', '#F6947F', '#C85050', '#B24A4F']

for gdf_, i in zip(gdf, range(len(gdf))):
    nbs = gdf_.set_index('cd')['nb']
    cm = colormap.LinearColormap(color_code, index=breaks, caption='cm')
    cl = folium.GeoJson(
        gdf_,
        style_function=lambda feature: {
            'fillColor': cm(nbs[feature['cd']]),
            'color': 'grey',
            'weight': 0.5,
            'fillOpacity': 0.9
        }
    )
    m.add_child(cl)
    m.add_child(BindColormap(cl,cl))


#folium.LayerControl('topright', collapsed=True).add_to(m)
m.save('test.html')
new = 2  # open in a new tab, if possible
url = "file://" + os.getcwd() + "/test.html"
webbrowser.open(url, new=new)