"""
Coverage disaggregation

"""
import os
import configparser
import glob
import fiona
import pandas as pd
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
from shapely.geometry import mapping

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def load_regions(directory):
#
    # regions = []

    shapefiles = glob.glob(os.path.join(directory, 'regions','*.shp'))

    # for path in shapefiles:
    #     with fiona.open(path, 'r') as source:
    #         for item in source:
    #             regions.append(item)

    regions = pd.concat([gpd.read_file(shp) for shp in shapefiles
                ]).pipe(gpd.GeoDataFrame)#[:13]

    #Originally in WGS84 - unprojected
    regions.crs = {'init' :'epsg:4326'}

    #Convert to projected coordinates
    regions= regions.to_crs({'init': 'epsg:3857'})

    regions["area"] = regions['geometry'].area #/ 10**6

    #Convert to projected coordinates
    regions= regions.to_crs({'init': 'epsg:4326'})

    return regions


def get_pop_density(regions, directory):

    path_settlements = os.path.join(directory,'settlements.tif')

    with rasterio.open(path_settlements) as src:
        affine = src.transform
        array = src.read(1)

        #no data is set to -999 - remove!!
        array[array < 0] = 0
        pops = [d['sum'] for d in zonal_stats(
            regions, array, stats=['sum'], affine=affine)]

    regions['population'] = pops

    regions['pop_density'] = regions['population'] / (regions['area'] / 1e6)

    return regions


def dissagregate_coverage(country, regions, coverage):


    # regions = [
    #     {'id':'a', 'pop':10,'pop_density': 30},
    #     {'id':'b', 'pop':20,'pop_density': 130},
    #     {'id':'c', 'pop':70,'pop_density': 330},
    #     {'id':'d', 'pop':40,'pop_density': 530},
    #     {'id':'e', 'pop':60,'pop_density': 630},
    # ]
    # regions = pd.DataFrame(regions)

    ranked_regions = regions.sort_values(by=['pop_density'], ascending=False)

    total_pop = regions['population'].sum()
    print('total_pop of {} is {}'.format(country, round(total_pop/1e6,1)))

    covered_population = total_pop * (coverage / 100)
    print('covered_population of {} is {}'.format(country, round(covered_population/1e6,1)))

    results = []

    covered = 0

    for index, row in ranked_regions.iterrows():
        # print(row)
        new_pop = int(round(row['population']))

        if new_pop > 0:
            #+20 70    90 <= 80
            if (covered + new_pop) <= covered_population:
                results.append(
                    {
                    'GID_2': row['GID_2'],
                    'pop_covered': new_pop,
                    'coverage': 1,
                    'coverage_%': 100,
                    }
                )
            else:
                # print('spillover')
                difference = covered_population - covered
                # print(difference, new_pop)
                coverage_perc = round((difference / new_pop) * 100, 1)
                # print(difference, covered_population, covered)
                # print('coverage_perc {}'.format(coverage_perc))
                results.append(
                    {
                    'GID_2': row['GID_2'],
                    'pop_covered': difference,
                    'coverage': 0,
                    'coverage_%': coverage_perc,
                    }
                )
        else:
            results.append(
                    {
                    'GID_2': row['GID_2'],
                    'pop_covered': 0,
                    'coverage_%': 0,
                    }
                )

        covered += new_pop
    results = pd.DataFrame(results)
    # print(len(regions), len(results))
    # regions = pd.concat([regions, results], axis=0)
    regions = pd.merge(regions, results, on='GID_2')
    # regions['coverage'] = results
    # df_col = pd.concat([df1,df2], axis=1)
    # print(pd.DataFrame(regions))
    # print(regions)

    return regions


if __name__ == '__main__':

    country = 'UGA'
    coverage = 78
    directory = os.path.join(DATA_INTERMEDIATE, country)

    regions = load_regions(directory)

    regions = get_pop_density(regions, directory)

    regions = dissagregate_coverage(country, regions, coverage)

    regions.to_file(os.path.join(DATA_INTERMEDIATE, country, 'disaggregation.shp'))
