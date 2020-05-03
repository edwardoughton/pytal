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

fig, axs = plt.subplots(4, 2, figsize=(20,20))

countries = [
    ('UGA', 0, 0, 'A'),
    ('MWI', 0, 1, 'B'),
    ('KEN', 1, 0, 'C'),
    ('SEN', 1, 1, 'D'),
    ('PAK', 2, 0, 'E'),
    ('ALB', 2, 1, 'F'),
    ('PER', 3, 0, 'G'),
    ('MEX', 3, 1, 'H'),
]

for country in countries:

    iso3 = country[0]
    x = country[1]
    y = country[2]
    plot_title = country[3]

    country_path = os.path.join(DATA_INTERMEDIATE, iso3)

    region = gpd.read_file(os.path.join(country_path, 'national_outline.shp'))
    region.plot(facecolor="none", edgecolor='black', lw=0.7, ax=axs[x, y])

    core_edges = gpd.read_file(os.path.join(country_path, 'network', 'core_edges.shp'))
    core_nodes = gpd.read_file(os.path.join(country_path, 'network', 'core_nodes.shp'))

    existing_edges = core_edges.loc[core_edges['source'] == 'existing']
    existing_edges.plot(facecolor="none", edgecolor='red', lw=1, ax=axs[x, y])
    existing_nodes = core_nodes.loc[core_nodes['source'] == 'existing']
    existing_nodes.plot(edgecolor='red', markersize=40, marker='.', ax=axs[x, y])

    new_edges = core_edges.loc[core_edges['source'] == 'new']
    new_edges.plot(facecolor="none", edgecolor='orange', lw=1, ax=axs[x, y])
    new_nodes = core_nodes.loc[core_nodes['source'] == 'new']
    new_nodes.plot(edgecolor='orange', markersize=40, marker='.', ax=axs[x, y])

    regional_edges = gpd.read_file(os.path.join(country_path, 'network', 'regional_edges.shp'))
    regional_edges.plot(facecolor="none", edgecolor='green', lw=0.5, ax=axs[x, y])
    regional_nodes = gpd.read_file(os.path.join(country_path, 'network', 'regional_nodes.shp'))
    regional_nodes.plot(edgecolor='green', markersize=40, marker='.', ax=axs[x, y])

    axs[x, y].set_title(plot_title)
    ctx.add_basemap(axs[x, y], crs=region.crs)

fig.tight_layout()
plt.savefig(os.path.join(BASE_PATH, '..', 'vis', 'figures', 'test.png'))
