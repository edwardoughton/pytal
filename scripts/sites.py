"""
Site evaluation script.

The purpose is to obtain all site information from different sources,
and compare the results to understand how the openly available site data
performs in different locations.

Written by Ed Oughton.

February 2020

"""
import os
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
FIGURES_OUT = os.path.join(BASE_PATH,'..', 'vis', 'figures')

def load_sites_senegal(path, existing_crs, new_crs, x, y, network):
    """
    Load data for senegal.

    """
    sites = pd.read_csv(path, encoding = "ISO-8859-1")

    if int(network) > 0:
        sites = sites[sites.net == network]

    sites = gpd.GeoDataFrame(
        sites, geometry=gpd.points_from_xy(sites[x], sites[y]))

    sites.crs = existing_crs

    sites = sites.to_crs(new_crs)

    return sites


def load_sites_canada(path, existing_crs, new_crs, x, y, network):
    """
    Load data for canada.

    """
    if os.path.basename(path) == 'Site_Data_Extract_subset.csv':
        fields = [x, y, 'LICENSEE']
        sites = pd.read_csv(path, usecols=fields, encoding = "ISO-8859-1")
        sites = sites[sites.LICENSEE.str.contains('TELUS')]
    else:
        fields = [x, y, 'net']
        sites = pd.read_csv(path, usecols=fields, encoding = "ISO-8859-1")
    # if any(int(i) > 0 for i in network):
        sites = sites[sites.net.isin(network)]

    sites = gpd.GeoDataFrame(
        sites, geometry=gpd.points_from_xy(sites[x], sites[y]))

    sites.crs = existing_crs

    sites = sites.to_crs(new_crs)

    return sites


def vis(data):
    """
    Visualize site data.

    """
    data['ARPU'] = data['mean_luminosity_km2'].apply(allocate_arpu)

    subset = data[['GID_2','population_km2', 'ARPU', 'real_data', 'opencellid', 'mozilla']]
    subset = subset[subset['population_km2'] < 1000]
    g = sns.pairplot(subset, hue='ARPU')
    g.savefig(os.path.join(FIGURES_OUT, 'pairplot.png'))

    print('Vis complete')


def allocate_arpu(x):
    """
    Allocate APRU based on luminosity per km^2.

    """
    if x > 5:
        return 'High'
    elif 1 < x <= 5:
        return 'Medium'
    else:
        return 'Low'


def run_senegal(senegal):
    """

    """
    for key, value in senegal.items():

        path = os.path.join(DATA_INTERMEDIATE, key, 'regional_data.csv')
        regional_data = pd.read_csv(path)

        path = os.path.join(DATA_INTERMEDIATE, key, 'regions_lowest', 'regions_2_{}.shp'.format(key))
        regions = gpd.read_file(path)

        column_keys = []

        for dataset in value:

            print('Working on {} with {}'.format(dataset[0], dataset[1]))

            path = dataset[1]

            sites = load_sites_senegal(
                path, dataset[2], dataset[3], dataset[4], dataset[5], dataset[7])

            f = lambda x:np.sum(sites.intersects(x))
            regions[dataset[6]] = regions['geometry'].apply(f)

            column_keys.append(dataset[6])

        to_merge = regions[[column_keys[0], column_keys[1], column_keys[2], 'GID_2']]

        to_write = pd.merge(regional_data, to_merge, on='GID_2', how='outer')

        to_write = to_write.drop_duplicates()

        vis(to_write)

        path = os.path.join(DATA_INTERMEDIATE, key, 'regional_data_with_sites.csv')
        to_write.to_csv(path, index=False)

    print('Senegal complete')


if __name__ == '__main__':

    # senegal = {
    #     'SEN': [
    #         ('SEN',
    #             os.path.join(DATA_RAW, 'real_site_data', 'SEN', 'Bilan_Couverture_Orange_Dec2017.csv'),
    #             'epsg:31028', 'epsg:4326', 'LONGITUDE', 'LATITUDE' ,'real_data', 0),
    #         ('SEN',
    #             os.path.join(DATA_INTERMEDIATE, 'SEN', 'sites_opencellid.csv'),
    #             'epsg:4326', 'epsg:4326', 'lon', 'lat', 'opencellid', 1),
    #         ('SEN',
    #             os.path.join(DATA_INTERMEDIATE, 'SEN', 'sites_mozilla.csv'),
    #             'epsg:4326', 'epsg:4326', 'lon', 'lat', 'mozilla', 1),
    #         ],
    #     }

    # run_senegal(senegal)

    canada = {'CAN': [
            #AWS 1-3 - 1700MHz + 2100MHz
            #BRS - 2500MHz
            #CELL - 800MHz
            #MBS - 700MHz
            #PCS - 1800MHz
            #WCS - 2300MHz
            ('CAN',
                os.path.join(DATA_RAW, 'real_site_data', 'CAN', 'Site_Data_Extract_subset.csv'),
                'epsg:4326', 'epsg:4326', 'LONGITUDE', 'LATITUDE' ,'real_data', [0]),
            ('CAN',
                os.path.join(DATA_INTERMEDIATE, 'CAN', 'sites_opencellid.csv'),
                'epsg:4326', 'epsg:4326', 'lon', 'lat', 'opencellid', [220,653]),
            ('CAN',
                os.path.join(DATA_INTERMEDIATE, 'CAN', 'sites_mozilla.csv'),
                'epsg:4326', 'epsg:4326', 'lon', 'lat', 'mozilla', [220,653]),
            ],
        }

    for key, value in canada.items():

        path = os.path.join(DATA_INTERMEDIATE, key, 'regional_data.csv')
        regional_data = pd.read_csv(path)

        path = os.path.join(DATA_INTERMEDIATE, key, 'regions_lowest', 'regions_2_{}.shp'.format(key))
        regions = gpd.read_file(path)

        column_keys = []

        for dataset in value:

            print('Working on {} with {}'.format(dataset[0], dataset[1]))

            path = dataset[1]

            sites = load_sites_canada(
                path, dataset[2], dataset[3], dataset[4], dataset[5], dataset[7])

            f = lambda x:np.sum(sites.intersects(x))
            regions[dataset[6]] = regions['geometry'].apply(f)

            column_keys.append(dataset[6])

        to_merge = regions[[column_keys[0], column_keys[1], column_keys[2], 'GID_2']]

        to_write = pd.merge(regional_data, to_merge, on='GID_2', how='outer')

        to_write = to_write.drop_duplicates()

        # vis(to_write)

        path = os.path.join(DATA_INTERMEDIATE, key, 'regional_data_with_sites.csv')
        to_write.to_csv(path, index=False)
