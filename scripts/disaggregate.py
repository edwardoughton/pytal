"""
Coverage disaggregation

"""
import os
import configparser
import glob
import fiona

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def load_regions(country):

    regions = []

    directory = os.path.join(DATA_INTERMEDIATE, country)

    paths = glob.glob(os.path.join(directory, 'regions','*.shp'))

    for path in paths:
        with fiona.open(path, 'r') as source:
            for item in source:
                regions.append(item)

    return regions


def get_pop_density(regions):

    regions = []

    #import pop density layer

    #use rasterio to get population

    #calc population density

    return regions


def dissagregate_coverage(regions, coverage):

    regions = []
    #rank regions based on population density
    #iterate through regions allocating coverage up until the coverage limit

    return


if __name__ == '__main__':

    country = 'MWI'

    regions = load_regions(country)

    print([r for r in regions])
