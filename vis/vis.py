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

import contextily as ctx

import matplotlib.gridspec as gridspec

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
EXPORT_FIGURES = os.path.join(BASE_PATH, '..', 'vis', 'figures')

if not os.path.exists(EXPORT_FIGURES):
    os.makedirs(EXPORT_FIGURES)

path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

if os.path.exists(path_countries):
    countries = gpd.read_file(path_countries)
else:
    print('Must generate global_countries.shp first' )

def prepare_data():

    global_data = []

    for name in countries.GID_0.unique():

        # if name not in ('CAN' , 'USA'):
        #     continue

        print('working on {}'.format(name))

        path_results = os.path.join(DATA_INTERMEDIATE, name, 'regional_data.csv')

        try:
            results = pd.read_csv(path_results)

            if len(results) == 0:
                continue

            global_data.append(results)

        except:

            region_paths = glob.glob(os.path.join(DATA_INTERMEDIATE, name, 'lowest_regions', '*.shp'))

            for region_path in region_paths:

                region = gpd.read_file(region_path)

                try:
                    no_data = [{
                        'GID_0': region.GID_0.values[0],
                        'GID_1': region.GID_1.values[0],
                        'GID_2': region.GID_2.values[0],
                        'median_luminosity': float('NaN'),
                        'sum_luminosity': float('NaN'),
                        'mean_luminosity_km2': float('NaN'),
                        'population': float('NaN'),
                        'area_km2': float('NaN'),
                        'population_km2': float('NaN'),
                    }]

                    no_data = pd.DataFrame(no_data)

                    global_data.append(no_data)

                except:
                    print('{} failed'.format(name))

            print('{} failed'.format(name))

    global_df = pd.concat(global_data, axis=0)

    return global_df


def plot_global_data(global_df, metric, title):

    global_df = global_df[['GID_1', 'GID_2', metric]]

    data_to_bin = global_df[~global_df[metric].isna()]

    labels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    bins = [
        -1,
        data_to_bin[metric].quantile(0.5),
        data_to_bin[metric].quantile(0.55),
        data_to_bin[metric].quantile(0.6),
        data_to_bin[metric].quantile(0.65),
        data_to_bin[metric].quantile(0.7),
        data_to_bin[metric].quantile(0.75),
        data_to_bin[metric].quantile(0.8),
        data_to_bin[metric].quantile(0.85),
        data_to_bin[metric].quantile(0.9),
        data_to_bin[metric].quantile(0.95),
        data_to_bin[metric].quantile(1)
    ]

    regions = gpd.read_file(os.path.join(DATA_INTERMEDIATE,'global_regions.shp'))

    regions_1 = regions.loc[regions['gid_region'] == 1]
    regions_1 = regions_1.merge(global_df, on='GID_1')

    regions_2 = regions.loc[regions['gid_region'] == 2]
    regions_2 = regions_2.merge(global_df, on='GID_2')

    regions = pd.concat([regions_1, regions_2], sort=True)

    regions.reset_index(drop=True,inplace=True)

    # missing_data = regions[regions[metric].isna()]

    fig, ax = plt.subplots(1, 1, figsize=(20,12))

    # from mpl_toolkits.axes_grid1 import make_axes_locatable
    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes("right", size="5%", pad=0.1)

    regions['bin'] = pd.cut(regions[metric], bins=bins, labels=labels).fillna(0)

    regions.plot(column='bin', ax=ax, cmap='inferno', linewidth=0, legend=True,
                legend_kwds={'label': title, 'orientation': "horizontal"})

    # missing_data.plot(ax=ax, facecolor='grey', linewidth=0)

    fig.savefig(os.path.join(EXPORT_FIGURES, '{}.pdf'.format(metric)))

    print('Completed plotting {}'.format(metric))


def find_country_list(continent_list):
    """

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    countries = gpd.read_file(path_processed)

    subset = countries.loc[countries['continent'].isin(continent_list)]

    country_list = []

    for name in subset.GID_0.unique():

        country_list.append(name)

    return country_list


def vis(metric, continent, country_list):

    path_results = os.path.join(BASE_PATH, '..', 'results',
        'results_business_model_options_72.csv')

    results = pd.read_csv(path_results)

    subset = results.loc[results['strategy'] == '5G_nsa_microwave_baseline']

    subset = subset.loc[subset['country'].isin(country_list)]

    region_path = os.path.join(DATA_INTERMEDIATE, 'global_regions_2.shp')#[:100]

    regions = gpd.read_file(region_path)

    regions['region_id'] = regions.apply(find_region_level, axis=1)

    regions = regions.merge(subset, left_on='region_id', right_on='region_level')

    regions.reset_index(drop=True, inplace=True)

    # if metric == 'viability':
    #     regions[metric] == (regions[metric]-regions[metric].min())/(regions[metric].max()-regions[metric].min())

    labels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    bins = [
        -1,
        regions[metric].quantile(0),
        regions[metric].quantile(0.1),
        regions[metric].quantile(0.2),
        regions[metric].quantile(0.3),
        regions[metric].quantile(0.4),
        regions[metric].quantile(0.5),
        regions[metric].quantile(0.6),
        regions[metric].quantile(0.7),
        regions[metric].quantile(0.8),
        regions[metric].quantile(0.9),
        regions[metric].quantile(1)
    ]

    fig, ax = plt.subplots(1, 1, figsize=(8,12))
    # print(pd.cut(regions[metric], bins=10))
    # regions['bin'] = pd.qcut(regions['viability'], 4, labels=['Delta', "Gamma", "Beta", "Alpha"])

    regions['bin'] = pd.cut(regions[metric], bins=bins, labels=labels).fillna(0)

    regions.plot(column='bin', ax=ax, cmap='inferno', linewidth=0, legend=True)

    ctx.add_basemap(ax, crs=regions.crs)

    fig.savefig(os.path.join(EXPORT_FIGURES, '{}_{}.pdf'.format(metric, continent)))

    return 0


def find_region_level(x):

    # if 'GID_4' in x:
    #     if x['GID_4'] is not None:
    #         return x['GID_4']
    # elif 'GID_3' in x:
    #     if x['GID_3'] is not None:
    #         return x['GID_3']
    if x.GID_2 is not None:
        return x.GID_2
    elif x.GID_1 is not None:
        return x.GID_1
    else:
        return x['GID_0']


if __name__ == '__main__':

    # graphics = [
    #     ('Africa', 'cost_km2'),
    #     # ('Africa', 'viability'),
    #     ('South America', 'cost_km2'),
    #     # ('South America', 'cost_km2'),
    # ]

    # for graphic in graphics:

    #     continent = graphic[0]

    #     country_list = find_country_list([continent])

    #     metric = graphic[1]

    #     global_df = vis(metric, continent, country_list)

    global_df = prepare_data()

    plot_global_data(global_df, 'mean_luminosity_km2', 'Mean Night Time Luminosity (per km^2)')

    # plot_global_data(global_df, 'population_km2', 'Population Density (Persons per km^2)')
