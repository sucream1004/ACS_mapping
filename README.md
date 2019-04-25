# ACS NYC mapper
- This is the simple code to plot interactive choropleth map using American Community Survey(census).
- The variable code can be found at [acs2017](https://api.census.gov/data/2017/acs/acs5/variables.html).

## Requirement
- pandas
- geopandas

### These are might be followed by above packages or anaconda
- numpy
- shapely

`conda install -c anaconda geopandas pandas numpy shapely -y`

## Example
`python acs_mapper_choropleth.py B01001_001E #Total population` \
<br>
Showing B01001_001E variable by Quantile schema. <br>

![img1](img/img1.png)
- test.html is created in the current directory. Sorry!

## Reference
- [folium](https://github.com/python-visualization/folium)
