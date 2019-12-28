import os
import sys
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd
import glob
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator
from matplotlib.ticker import ScalarFormatter
from matplotlib.patches import Patch
import matplotlib.patches
import matplotlib.transforms as transforms
from matplotlib.colors import LinearSegmentedColormap

import matplotlib.gridspec as gridspec

# from utils import load_config #,create_folder_lookup,map_roads,line_length

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

if os.path.exists(path_countries):
    countries = gpd.read_file(path_countries)
else:
    print('Must generate global_countries.shp first' )

#GID_0	GID_1	GID_2	median_luminosity	sum_luminosity
global_data = []

num = 0
for name in countries.GID_0.unique():

    # if name not in ('CAN' , 'USA'):
    #     continue
    print('working on {}'.format(name))

    path_results = os.path.join(DATA_INTERMEDIATE, name, 'luminosity.csv')

    try:
        luminosity = pd.read_csv(path_results)

        if len(luminosity) == 0:
            continue

        global_data.append(luminosity)

        # print(global_data)

    except:

        region_paths = glob.glob(os.path.join(DATA_INTERMEDIATE, name, 'regions', '*.shp'))

        for region_path in region_paths:

            region = gpd.read_file(region_path)

            no_data = [{
                'GID_0': region.GID_0.values[0],
                'GID_1': region.GID_1.values[0],
                'GID_2': region.GID_2.values[0],
                'median_luminosity': float('NaN'),
                'sum_luminosity': 0,
            }]

            no_data = pd.DataFrame(no_data)
            # print(no_data)
            global_data.append(no_data)

        print('{} failed'.format(name))


global_df = pd.concat(global_data, axis=0)

metric = 'median_luminosity' # 'sum_luminosity' #
global_df = global_df[['GID_2', metric]]

data_to_bin = global_df[~global_df[metric].isna()]
print(data_to_bin.describe())
labels = [0, 1, 2, 3, 4, 5]
# label_names = ['Very Low','Low','Medium','High','Very high']
# bins = [-1, data_to_bin[metric].quantile(0.2),
#             data_to_bin[metric].quantile(0.4),
#             data_to_bin[metric].quantile(0.6),
#             data_to_bin[metric].quantile(0.8),
#             data_to_bin[metric].quantile(1)
#             ]
label_names = ['Very Low','Low','Medium','High', 'Very High', 'Maximum']
bins = [
    -1,
    data_to_bin[metric].quantile(0.5),
    data_to_bin[metric].quantile(0.6),
    data_to_bin[metric].quantile(0.7),
    data_to_bin[metric].quantile(0.8),
    data_to_bin[metric].quantile(0.9),
    data_to_bin[metric].quantile(1)
]
color_scheme_map =  ['#fee5d9','#fcae91','#fb6a4a','#de2d26','#a50f15', '#4b070a'] # ['#feedde','#fdbe85','#fd8d3
cmap = LinearSegmentedColormap.from_list(name='continents', colors=color_scheme_map)

coastlines = gpd.read_file(os.path.join(DATA_INTERMEDIATE,'global_regions.shp'))

# coastlines.crs = {'init' :'epsg:4326'}

# coastlines= coastlines.to_crs({'init': 'epsg:3857'})

coastlines = coastlines.merge(global_df, on='GID_2')

# coastlines["area_km2"] = coastlines['geometry'].area / 10**6

# coastlines["sum_luminosity_km2"] = coastlines['sum_luminosity'] / coastlines["area_km2"]

# metric = 'sum_luminosity_km2'

# coastlines= coastlines.to_crs({'init': 'epsg:4326'})

print(coastlines.describe())
missing_data = coastlines[coastlines[metric].isna()]

fig, ax = plt.subplots(1, 1, figsize=(20,12))

coastlines['bin'] = pd.cut(coastlines[metric], bins=bins, labels=labels).fillna(0)

coastlines.plot(column='bin',ax=ax,cmap=cmap,linewidth=0)

missing_data.plot(ax=ax, facecolor='grey' ,linewidth=0)

legend_elements = [
    Patch(facecolor=color_scheme_map[0],label=label_names[0]),
                  Patch(facecolor=color_scheme_map[1],label=label_names[1]),
                  Patch(facecolor=color_scheme_map[2],label=label_names[2]),
                  Patch(facecolor=color_scheme_map[3],label=label_names[3]),
                  Patch(facecolor=color_scheme_map[4],label=label_names[4]),
                  Patch(facecolor=color_scheme_map[5],label=label_names[5])
                  ]

legend = ax.legend(handles=legend_elements, shadow=True,
                   fancybox=True, facecolor='#fefdfd', prop={'size':8}, loc='lower left')

ax.set_facecolor('lightgrey')

plt.show()
