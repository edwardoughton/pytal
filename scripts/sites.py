"""
Site evaluation script.

The purpose is to obtain all site information from different sources,
and compare the results to understand how the openly available site data
performs in different locations.

Written by Ed Oughton.

February 2020

"""
import os
import csv
import json
import configparser
import numpy as np
import pandas as pd
from shapely.geometry import MultiPolygon, shape, mapping
from shapely.ops import transform, cascaded_union
import pyproj
import rasterio
from rasterstats import zonal_stats
from rasterio.mask import mask
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from functools import partial
from sklearn.linear_model import LinearRegression

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
FIGURES_OUT = os.path.join(BASE_PATH,'..', 'vis', 'figures')


def process_country_shapes(country):
    """
    Creates a single national boundary for the desired country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']

    path = os.path.join(DATA_RAW, 'real_site_data', iso3)
    shape_path = os.path.join(path, 'national_outline.shp')

    if not os.path.exists(shape_path):

        print('----')
        print('Working on processing country shape')

        if not os.path.exists(path):
            print('Creating directory {}'.format(path))
            os.makedirs(path)

        print('Loading all country shapes')
        path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
        countries = gpd.read_file(path)

        print('Getting specific country shape for {}'.format(iso3))
        single_country = countries[countries.GID_0 == iso3]

        print('Excluding small shapes')
        single_country['geometry'] = single_country.apply(
            exclude_small_shapes, axis=1)

        print('Simplifying geometries')
        single_country['geometry'] = single_country.simplify(
            tolerance = 0.005,
            preserve_topology=True).buffer(0.01).simplify(
            tolerance = 0.005,
            preserve_topology=True
        )

        print('Adding ISO country code and other global information')
        glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
        load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")
        single_country = single_country.merge(
            load_glob_info,left_on='GID_0', right_on='ISO_3digit')

        print('Exporting processed country shape')
        single_country.to_file(shape_path, driver='ESRI Shapefile')

    return print('Processing country shape complete')


def process_regions(country):
    """
    Function for processing the lowest desired subnational regions for the
    chosen country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    regions = []

    iso3 = country['iso3']
    level = country['regional_level']

    print('----')
    print('Working on {} level {}'.format(iso3, level))

    folder = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions')
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path_processed = os.path.join(folder, filename)

    if not os.path.exists(path_processed):

        filename = 'gadm36_{}.shp'.format(level)
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        print('Subsetting {} level {}'.format(iso3, level))
        regions = regions[regions.GID_0 == iso3]

        print('Excluding small shapes')
        regions['geometry'] = regions.apply(exclude_small_shapes, axis=1)

        print('Simplifying geometries')
        regions['geometry'] = regions.simplify(
            tolerance = 0.005,
            preserve_topology=True).buffer(0.01).simplify(
                tolerance = 0.005,
                preserve_topology=True
            )
        try:
            print('Writing {} shapes to file'.format(iso3))
            regions.to_file(path_processed, driver='ESRI Shapefile')
        except:
            print('Unable to write {}'.format(filename))
            pass


def exclude_small_shapes(x):
    """
    Remove small multipolygon shapes.

    Parameters
    ---------
    x : polygon
        Feature to simplify.

    Returns
    -------
    MultiPolygon : MultiPolygon
        Shapely MultiPolygon geometry without tiny shapes.

    """
    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        return x.geometry

    # if its a multipolygon, we start trying to simplify
    # and remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        area1 = 0.01
        area2 = 50

        # dont remove shapes if total area is already very small
        if x.geometry.area < area1:
            return x.geometry
        # remove bigger shapes if country is really big

        if x['GID_0'] in ['CHL','IDN']:
            threshold = 0.01
        elif x['GID_0'] in ['RUS','GRL','CAN','USA']:
            threshold = 0.01

        elif x.geometry.area > area2:
            threshold = 0.1
        else:
            threshold = 0.001

        # save remaining polygons as new multipolygon for
        # the specific country
        new_geom = []
        for y in x.geometry:
            if y.area > threshold:
                new_geom.append(y)

        return MultiPolygon(new_geom)


def process_settlement_layer(country):
    """
    Clip the settlement layer to the chosen country boundary and place in
    desired country folder.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']

    path_country = os.path.join(DATA_RAW, 'real_site_data', iso3)
    shape_path = os.path.join(path_country, 'settlements.tif')

    if not os.path.exists(shape_path):

        print('----')
        print('Working on settlement layer')

        path_settlements = os.path.join(DATA_RAW,'settlement_layer',
            'ppp_2020_1km_Aggregated.tif')

        settlements = rasterio.open(path_settlements, 'r+')
        settlements.nodata = 255
        settlements.crs = {"init": "EPSG:4326"}

        path_country = os.path.join(DATA_RAW, 'real_site_data', iso3,
            'national_outline.shp')

        if os.path.exists(path_country):
            country = gpd.read_file(path_country)
        else:
            print('Must generate national_outline.shp first' )

        bbox = country.envelope
        geo = gpd.GeoDataFrame()

        geo = gpd.GeoDataFrame({'geometry': bbox})

        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        #chop on coords
        out_img, out_transform = mask(settlements, coords, crop=True)

        # Copy the metadata
        out_meta = settlements.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": 'EPSG:4326'})

        with rasterio.open(shape_path, "w", **out_meta) as dest:
                dest.write(out_img)

    return print('Completed processing of settlement layer')


def get_regional_data(country, regions):
    """
    Extract regional data including luminosity and population.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']
    level = country['regional_level']

    path_settlements = os.path.join(DATA_RAW,'real_site_data', iso3,
        'settlements.tif')

    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'), # source coordinate system
        pyproj.Proj(init='epsg:3857')) # destination coordinate system

    results = []

    for index, region in regions.iterrows():

        with rasterio.open(path_settlements) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            #get luminosity values
            population_summation = [d['sum'] for d in zonal_stats(
                region['geometry'], array, stats=['sum'], affine=affine)][0]

        geom = transform(project, region['geometry'])

        area_km2 = geom.area / 10**6

        gid_level = 'GID_{}'.format(level)

        if not population_summation == None:
            population_km2 = population_summation / area_km2
        else:
            population_km2 = 0

        results.append({
            'type': 'Feature',
            'geometry': region['geometry'],
            'properties': {
                'GID_0': region['GID_0'],
                gid_level: region[gid_level],
                'population': population_summation,
                'area_km2': area_km2,
                'population_km2': population_km2,
                'sites': region['sites'],
                'sites_km2': region['sites'] / area_km2,
            },
        })

    results_df = gpd.GeoDataFrame.from_features(results)

    return results_df


def australia(country):
    """

    """
    iso3 = country['iso3']
    level = country['regional_level']

    filename = 'regions_{}_{}_with_sites.shp'.format(level, iso3)
    path_processed = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)
    regions = gpd.read_file(path)#[:10]

    filename = 'site.csv'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'spectra_rrl', filename)

    sites = []

    with open(path, 'r', errors='ignore') as source:
        reader = csv.DictReader(source)
        for idx, item in enumerate(reader):
            try:
                sites.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': (
                            float(item['LONGITUDE']),
                            float(item['LATITUDE'])
                        )
                    },
                    'properties': {
                        'site_id': item['SITE_ID'],
                    }
                })
            except:
                pass

    sites = gpd.GeoDataFrame.from_features(sites)

    sites.crs = 'EPSG:4326'

    filename = 'sites.shp'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)
    sites.to_file(path)

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = get_regional_data(country, regions)

    regions.crs = 'EPSG:4326'

    regions['country'] = iso3

    regions.to_file(path_processed)

    return regions


def canada(country):
    """
    According to statistica:

    Number of wireless towers in Canada in 2018, by provider

    provider	lte	umts	cdma	gsm
    Bell	4,204	3,622	-	-
    Bell/Telus (FastRoam)	6,743	9,015	90	-
    EastLink	168	155	-	-
    Freedom Mobile*	1,722	1,781	-	-
    MTS	92	22	-	-
    Rogers Wireless	4,147	3,975	-	1,792
    SaskTel	206	295	-	-
    Telus	5,370	5,618	93	-
    Videotron	337	502	-	-

    total	22,989	24,985	183	1,792

    """
    iso3 = country['iso3']
    level = country['regional_level']

    filename = 'regions_{}_{}_with_sites.shp'.format(level, iso3)
    path_processed = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)
    regions = gpd.read_file(path)#[:10]

    filename = 'Site_Data_Extract.csv'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)

    cellular_bands = [
            'AWS', #1-3 - 1700MHz + 2100MHz
            'BRS', #- 2500MHz
            'CELL', # - 800MHz
            'MBS', #- 700MHz
            'PCS', #- 1800MHz
            'WCS', #- 2300MHz
    ]

    sites = []

    with open(path, 'r', errors='ignore') as source:
        reader = csv.DictReader(source)
        for idx, item in enumerate(reader):
            if item['SERVICE'] in cellular_bands:
                sites.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': (
                            float(item['LONGITUDE']),
                            float(item['LATITUDE'])
                        )
                    },
                    'properties': {
                        'site_id': idx,
                    }
                })

    # print('Loaded {} total cells'.format(len(sites)))

    # sites = sites#[:1000]

    # print('Subseeting {} cells'.format(len(sites)))

    # sites = process_asset_data(country, regions, sites)

    # print('Processed down to {} sites'.format(len(sites)))

    sites = gpd.GeoDataFrame.from_features(sites)

    sites.crs = 'EPSG:4326'
    filename = 'sites_all.shp'
    folder = os.path.join(DATA_RAW, 'real_site_data', iso3, 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)
    sites.to_file(path)

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = get_regional_data(country, regions)

    regions['country'] = iso3

    regions.crs = 'EPSG:4326'
    regions.to_file(path_processed)

    return regions


def kenya(country):
    """

    """
    iso3 = country['iso3']
    level = country['regional_level']

    filename = 'regions_{}_{}_with_sites.shp'.format(level, iso3)
    path_processed = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)
    regions = gpd.read_file(path)

    filename = 'Operators_Mobile_Transmitters_Data.csv'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)

    sites = []

    with open(path, 'r', errors='ignore') as source:
        reader = csv.DictReader(source)
        for idx, item in enumerate(reader):
            try:
                sites.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': (
                            float(item['LONGITUDE']),
                            float(item['LATITUDE'])
                        )
                    },
                    'properties': {
                        'site_id': item['SiteID'],
                    }
                })
            except:
                pass

    sites = gpd.GeoDataFrame.from_features(sites)

    sites.crs = 'EPSG:4326'

    filename = 'sites.shp'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)
    sites.to_file(path)

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = get_regional_data(country, regions)

    regions.crs = 'EPSG:4326'

    regions['country'] = iso3

    regions.to_file(path_processed)

    return regions


def great_britain(country):
    """

    """
    iso3 = country['iso3']
    level = country['regional_level']

    filename = 'regions_{}_{}_with_sites.shp'.format(level, iso3)
    path_processed = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)
    regions = gpd.read_file(path)#[:10]

    filename = 'sitefinder.csv'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)

    sites = []

    with open(path, 'r', errors='ignore') as source:
        reader = csv.DictReader(source)
        for idx, item in enumerate(reader):
            try:
                sites.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': (
                            float(item['Sitelng']),
                            float(item['Sitelat'])
                        )
                    },
                    'properties': {
                        'site_id': item['Sitengr'],
                    }
                })
            except:
                pass

    sites = gpd.GeoDataFrame.from_features(sites)#[:100]

    sites.crs = 'EPSG:4326'

    filename = 'sites.shp'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)
    sites.to_file(path)

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = get_regional_data(country, regions)

    regions.crs = 'EPSG:4326'

    regions['country'] = iso3

    regions.to_file(path_processed)

    return regions


def netherlands(country):
    """

    """
    iso3 = country['iso3']
    level = country['regional_level']

    filename = 'regions_{}_{}_with_sites.shp'.format(level, iso3)
    path_processed = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)
    regions = gpd.read_file(path)

    filename = '1_antennetotalen_juli_2017.csv'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)

    sites = []

    with open(path, 'r', errors='ignore') as source:
        reader = csv.DictReader(source)
        for idx, item in enumerate(reader):
            try:
                sites.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': (
                            float(item['X']),
                            float(item['Y'])
                        )
                    },
                    'properties': {
                        'site_id': idx,
                    }
                })
            except:
                pass

    sites = gpd.GeoDataFrame.from_features(sites)

    sites.crs = 'epsg:28992'

    sites = sites.to_crs({'init': 'EPSG:4326'})

    filename = 'sites.shp'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)
    sites.to_file(path)

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = get_regional_data(country, regions)

    regions.crs = 'EPSG:4326'

    regions['country'] = iso3

    regions.to_file(path_processed)

    return regions


def senegal(country):
    """

    """
    iso3 = country['iso3']
    level = country['regional_level']

    filename = 'regions_{}_{}_with_sites.shp'.format(level, iso3)
    path_processed = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'regions', filename)
    regions = gpd.read_file(path)

    filename = 'Bilan_Couverture_Orange_Dec2017.csv'
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, filename)

    sites = []

    with open(path, 'r', errors='ignore') as source:
        reader = csv.DictReader(source)
        for item in reader:
            sites.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': (
                        float(item['LONGITUDE']),
                        float(item['LATITUDE'])
                    )
                },
                'properties': {
                    'site_id': item['Site_Name'],
                }
            })

    sites = gpd.GeoDataFrame.from_features(sites)

    sites.crs = 'epsg:31028'

    sites = sites.to_crs('EPSG:4326')

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = get_regional_data(country, regions)

    regions.crs = 'EPSG:4326'

    regions['country'] = iso3

    regions.to_file(path_processed)

    return regions


def process_asset_data(country, regions, data):
    """
    Add buffer to each site, dissolve overlaps and take centroid.

    """
    iso3 = country['iso3']
    level = country['regional_level']

    level = 'GID_{}'.format(level)

    output = []

    for idx, region in regions.iterrows():

        folder = os.path.join(DATA_RAW, 'real_site_data', iso3, 'sites', 'by_region')
        path = os.path.join(folder, region[level] + '.shp')

        if not os.path.exists(path):

            geom = region['geometry']

            sites = gpd.GeoDataFrame.from_features(data)

            sites.crs = 'EPSG:4326'
            regions.crs = 'EPSG:4326'

            sites = sites[sites.intersects(geom)]

            if len(sites) > 0:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                sites.to_file(path)
            else:
                continue
        else:
            sites = gpd.read_file(path)

        project = partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:4326'), # source coordinate system
            pyproj.Proj(init='epsg:3857')) # destination coordinate system

        buffered_assets = []

        for idx, asset in sites.iterrows():

            asset_geom = asset['geometry']
            geom = transform(project, asset_geom)

            buffered_geom = geom.buffer(80)

            buffered_assets.append({
                'type': 'Feature',
                'geometry': mapping(asset['geometry']),
                'buffer': buffered_geom,
                'properties': {
                    'site_id': asset['site_id'],
                }
            })

        assets_seen = set()

        project = partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:3857'), # source coordinate system
            pyproj.Proj(init='epsg:4326')) # destination coordinate system

        for asset in buffered_assets:
            if asset['properties']['site_id'] in assets_seen:
                continue
            assets_seen.add(asset['properties']['site_id'])
            touching_assets = []
            for other_asset in buffered_assets:
                if asset['buffer'].intersects(other_asset['buffer']):
                    touching_assets.append(other_asset)
                    assets_seen.add(other_asset['properties']['site_id'])

            dissolved_shape = cascaded_union([a['buffer'] for a in touching_assets])
            final_centroid = dissolved_shape.centroid
            final_centroid = transform(project, final_centroid)
            output.append({
                'type': "Feature",
                'geometry': {
                    "type": "Point",
                    "coordinates": [
                        final_centroid.coords[0][0],
                        final_centroid.coords[0][1]
                    ],
                },
                'properties':{
                    'site_id': asset['properties']['site_id'],
                }
            })

    return output


def vis(country, data):
    """
    Visualize site data.

    """
    iso3 = country['iso3']

    subset = data[['population_km2', 'sites_km2']]

    subset = subset.dropna()

    g = sns.pairplot(subset)

    folder = os.path.join(DATA_RAW, 'real_site_data', iso3, 'figures')

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = '{}.png'.format(iso3)
    g.savefig(os.path.join(folder, filename))

    print('Vis complete')


def vis_panel(data):
    """
    Visualize site data.

    """

    subset = data[['population_km2', 'sites_km2', 'country']]

    subset = subset.dropna()

    g = sns.lmplot(x="population_km2", y="sites_km2", col="country",
            data=subset, col_wrap=2, height=3)

    g.set(xlim=(0,1000), ylim=(0,5))

    folder = os.path.join(DATA_RAW, 'real_site_data')

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = 'panel_plot.png'
    g.savefig(os.path.join(folder, filename))

    plt.clf()

    print('Vis complete')


def regression(data, folder, iso3):

    print('Working on regression')
    data = data.loc[data['country'] == iso3]

    #shuffle dataframe
    data = data.sample(frac=1)

    #use 80% for model, 20% for validation
    data_split = [80, 20]

    segment_sample = int(round(len(data)/(100/data_split[0])))

    #subset
    data_80 = data[:segment_sample]
    data_20 = data[segment_sample:]

    X = data_80['population_km2'].values.reshape(-1, 1)  # values converts it into a numpy array
    Y = data_80['sites_km2'].values.reshape(-1, 1)  # -1 means that calculate the dimension of rows, but have 1 column
    linear_regressor = LinearRegression()  # create object for the class
    linear_regressor.fit(X, Y)  # perform linear regression
    Y_pred = linear_regressor.predict(X)  # make predictions

    plt.scatter(X, Y)
    plt.plot(X, Y_pred, color='red')
    plt.title('Population Density Vs Cell Density', fontsize=14)
    plt.xlabel('Population Density (persons per km^2)', fontsize=14)
    plt.ylabel('Cell Density (cells per km^2)', fontsize=14)
    plt.grid(True)
    filename = 'regression_x_y.png'
    plt.savefig(os.path.join(folder, iso3, filename))

    plt.clf()

    X = data_20['population_km2'].values.reshape(-1, 1)
    Y = data_20['sites_km2'].values.reshape(-1, 1)
    Y_pred = linear_regressor.predict(X)

    plt.scatter(Y, Y_pred)
    plt.title('Cell Density Vs Predicted Cell Density', fontsize=14)
    plt.xlabel('Cell Density (cells per km^2)', fontsize=14)
    plt.ylabel('Predicted Cell Density (cells per km^2)', fontsize=14)
    plt.grid(True)

    filename = 'regression_y_pred_y.png'
    plt.savefig(os.path.join(folder, iso3,filename))

    plt.clf()

    return print('Regression complete')

if __name__ == '__main__':

    folder = os.path.join(DATA_RAW, 'real_site_data')

    # countries = [
    #     # {'iso3': 'AUS', 'iso2': 'AU', 'regional_level': 2, 'regional_hubs_level': 1},
    #     {'iso3': 'CAN', 'iso2': 'CA', 'regional_level': 2, 'regional_hubs_level': 1},
    #     # {'iso3': 'GBR', 'iso2': 'GB', 'regional_level': 2, 'regional_hubs_level': 1},
    #     # {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2, 'regional_hubs_level': 1},
    #     # {'iso3': 'NLD', 'iso2': 'ND', 'regional_level': 2, 'regional_hubs_level': 1},
    #     # {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_hubs_level': 1},
    #     ]

    # for country in countries:

    #     iso3 = country['iso3']

    #     print('Processing country outline')
    #     process_country_shapes(country)

    #     print('Processing regions')
    #     process_regions(country)

    #     print('Processing settlement layer')
    #     process_settlement_layer(country)

    #     print('Processing country sites data')

    #     if country['iso3'] == 'AUS':
    #         data_australia = australia(country)
    #         data_australia.drop('geometry', axis=1).to_csv(
    #             os.path.join(folder, iso3, 'results.csv'))
    #         vis(country, data_australia)

    #     if country['iso3'] == 'CAN':
    #         data_canada = canada(country)
    #         data_canada.drop('geometry',axis=1).to_csv(
    #             os.path.join(folder, iso3, 'results.csv'))
    #         vis(country, data_canada)

    #     if country['iso3'] == 'GBR':
    #         data_great_britain = great_britain(country)
    #         data_great_britain.drop(
    #             'geometry',axis=1).to_csv(
    #             os.path.join(folder, iso3, 'results.csv'))
    #         vis(country, data_great_britain)

    #     if country['iso3'] == 'KEN':
    #         data_kenya = kenya(country)
    #         data_kenya.drop(
    #             'geometry',axis=1).to_csv(
    #             os.path.join(folder, iso3, 'results.csv'))
    #         vis(country, data_kenya)

    #     if country['iso3'] == 'NLD':
    #         data_netherlands = netherlands(country)
    #         data_netherlands.drop(
    #             'geometry',axis=1).to_csv(
    #             os.path.join(folder, iso3, 'results.csv'))
    #         vis(country, data_netherlands)

    #     if country['iso3'] == 'SEN':
    #         data_senegal = senegal(country)
    #         data_senegal.drop(
    #             'geometry',axis=1).to_csv(
    #             os.path.join(folder, iso3, 'results.csv'))
    #         vis(country, data_senegal)

    folder = os.path.join(DATA_RAW, 'real_site_data')

    all_files = [
        ('AUS', 'results.csv'),
        ('CAN', 'results.csv'),
        ('GBR', 'results.csv'),
        ('KEN', 'results.csv'),
        ('NLD', 'results.csv'),
        ('SEN', 'results.csv'),
    ]

    data = []

    for file_tuple in all_files:
        filename = os.path.join(folder, file_tuple[0], file_tuple[1])
        df = pd.read_csv(filename, index_col=None, header=0)
        data.append(df)

    data = pd.concat(data, axis=0, ignore_index=True)

    vis_panel(data)

    for iso3 in all_files:
        regression(data, folder, iso3[0])
