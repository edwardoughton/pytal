"""
Visualize core and regional fiber networks.

"""
import os
import configparser
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.colors
# import seaborn as sns


CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')

fig, axs = plt.subplots(4, 2, figsize=(20, 20))

countries = [
    ('UGA', 0, 0, 'Uganda (C1)', 3),
    ('MWI', 0, 1, 'Malawi (C1)', 3.8),
    ('KEN', 1, 0, 'Kenya (C2)', 5),
    ('SEN', 1, 1, 'Senegal (C2)', 3),
    ('PAK', 2, 0, 'Pakistan (C3)', 7.5),
    ('ALB', 2, 1, 'Albania (C4)', 2),
    ('PER', 3, 0, 'Peru (C5)', 9),
    ('MEX', 3, 1, 'Mexico (C6)', 10),
]

for country in countries:

    iso3 = country[0]
    x = country[1]
    y = country[2]
    plot_title = country[3]
    buff_value = country[4]

    country_path = os.path.join(DATA_INTERMEDIATE, iso3)

    region = gpd.read_file(os.path.join(country_path, 'national_outline.shp'))
    region.plot(facecolor="none", edgecolor='grey', lw=1.2, ax=axs[x, y])

    core_edges = gpd.read_file(os.path.join(country_path, 'network', 'core_edges.shp'))
    core_nodes = gpd.read_file(os.path.join(country_path, 'network', 'core_nodes.shp'))

    existing_edges = core_edges.loc[core_edges['source'] == 'existing']
    existing_edges.plot(facecolor="none", edgecolor='black', lw=1.5, ax=axs[x, y])
    existing_nodes = core_nodes.loc[core_nodes['source'] == 'existing']
    existing_nodes.plot(edgecolor='black', markersize=40, marker='.', ax=axs[x, y])

    new_edges = core_edges.loc[core_edges['source'] == 'new']
    new_edges.plot(facecolor="none", edgecolor='red', lw=1.5, ax=axs[x, y])
    new_nodes = core_nodes.loc[core_nodes['source'] == 'new']
    new_nodes.plot(edgecolor='red', markersize=40, marker='.', ax=axs[x, y])

    regional_edges = gpd.read_file(os.path.join(country_path, 'network', 'regional_edges.shp'))
    regional_edges.plot(facecolor="none", edgecolor='orange', lw=0.8, ax=axs[x, y])
    regional_nodes = gpd.read_file(os.path.join(country_path, 'network', 'regional_nodes.shp'))
    regional_nodes.plot(edgecolor='yellow', markersize=40, marker='.', ax=axs[x, y])

    axs[x, y].set_title(plot_title)
    centroid = region['geometry'].values[0].representative_point().buffer(buff_value).envelope

    xmin = min([coord[0] for coord in centroid.exterior.coords])
    xmax = max([coord[0] for coord in centroid.exterior.coords])

    ymin = min([coord[1] for coord in centroid.exterior.coords])
    ymax = max([coord[1] for coord in centroid.exterior.coords])

    axs[x, y].set_xlim([xmin, xmax])
    axs[x, y].set_ylim([ymin, ymax])

    ctx.add_basemap(axs[x, y], crs=region.crs)

fig.tight_layout()

plt.savefig(os.path.join(BASE_PATH, '..', 'vis', 'figures', 'core_network_plot.png'))
