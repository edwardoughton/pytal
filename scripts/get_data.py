import os
import configparser
import pandas as pd
import numpy as np
import requests
import tarfile
import gzip
import shutil
import glob

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def get_nightlight_data(path, data_year):
    """
    Download the nighlight data from NOAA.

    As these files are large, they can take a couple of minutes to download.

    Parameters
    ----------
    path : string
        Path to the desired data location.

    """
    if not os.path.exists(path):
        os.makedirs(path)

    for year in [data_year]:
        year = str(year)
        url = ('https://ngdc.noaa.gov/eog/data/web_data/v4composites/F18'
                + year + '.v4.tar')
        target = os.path.join(path, year)
        if not os.path.exists(target):
            os.makedirs(target, exist_ok=True)
        target += '/nightlights_data'
        response = requests.get(url, stream=True)
        if not os.path.exists(target):
            if response.status_code == 200:
                print('Downloading data')
                with open(target, 'wb') as f:
                    f.write(response.raw.read())
    print('Data download complete')

    for year in [data_year]:
        print('Working on {}'.format(year))
        folder_loc = os.path.join(path, str(year))
        print(folder_loc)
        file_loc = os.path.join(folder_loc, 'nightlights_data')
        print(file_loc)
        # files = os.listdir(folder_loc)
        # print('len(files) == {}'.format(len(files)))
        # for file_type in files:
        #     print(file_type)
        #     if file_type.endswith('.tar'):
        print('Unzipping data')
        tar = tarfile.open(file_loc)
        tar.extractall(path=folder_loc)

        files = os.listdir(folder_loc)
        for filename in files:
            file_path = os.path.join(path, str(year), filename)
            if 'stable' in filename: # only need stable_lights
                if file_path.split('.')[-1] == 'gz':
                    # unzip the file is a .gz file
                    with gzip.open(file_path, 'rb') as f_in:
                        with open(file_path[:-3], 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
            # os.remove(file_path)

    return print('Downloaded and processed night light data')


def process_wb_survey_data(path):
    """
    Make sure you download the 2016-2017 Household LSMS survey
    data for Malawi from
    https://microdata.worldbank.org/index.php/catalog/lsms.
    It should be in ../data/input/LSMS/malawi-2016

    """
    # everything in comments I have not converted to Python3 but
    # they don't matter for predicting consumption
    # you can play around with the stata files and add additional
    # information to predict if you want
    file_path = os.path.join(path, 'IHS4 Consumption Aggregate.dta')

    ##Read file
    df = pd.read_stata(file_path)
    df['cons'] = df['rexpagg']/(365*df['adulteq'])
    df['cons'] = df['cons']*107.62/(116.28*166.12)

    ## Rename column
    df.rename(columns={'hh_wgt': 'weight'}, inplace=True)

    ## Subset desired columns
    df = df[['case_id', 'cons', 'weight', 'urban']]

    ##Read geolocated survey data
    df_geo = pd.read_stata('../data/input/LSMS/malawi_2016/HouseholdGeovariables_stata11/HouseholdGeovariablesIHS4.dta')

    ##Subset household coordinates
    df_cords = df_geo[['case_id', 'HHID', 'lat_modified', 'lon_modified']]
    df_cords.rename(columns={'lat_modified': 'lat', 'lon_modified': 'lon'}, inplace=True)
    # mwi13.hha <- read.dta('data/input/LSMS/MWI_2016_IHS-IV_v02_M_Stata/HH_MOD_A_FILT.dta')

    ##
    df_hhf = pd.read_stata('../data/input/LSMS/malawi_2016/HH_MOD_F.dta')
    # mwi13.room <- data.frame(hhid = mwi13.hhf$HHID, room = mwi13.hhf$hh_f10)
    # mwi13.metal <- data.frame(hhid = mwi13.hhf$HHID, metal = mwi13.hhf$hh_f10=='IRON SHEETS')

    ##Merge to add coordinates to
    df = pd.merge(df, df_cords[['case_id', 'HHID']], on='case_id')

    df_combined = pd.merge(df, df_cords, on=['case_id', 'HHID'])

    df_combined.drop('case_id', axis=1, inplace=True)

    df_combined.dropna(inplace=True) # can't use na values

    print('Combined shape is {}'.format(df_combined.shape))

    clust_cons_avg = df_combined.groupby(['lat', 'lon']).mean().reset_index()[['lat', 'lon', 'cons']]

    df_combined = pd.merge(df_combined.drop('cons', axis=1), clust_cons_avg, on=['lat', 'lon'])

    df_uniques = df_combined.drop_duplicates(subset=['lat', 'lon']); df_uniques.shape

    return print('Processed wb survey data')

if __name__ == '__main__':

    path = os.path.join(DATA_RAW, 'nightlights')
    get_nightlight_data(path, 2013)

    # path = os.path.join(DATA_RAW, 'LSMS', 'malawi_2016')
    # process_wb_survey_data(path)
