"""
Subscriptions module.

Written by Ed Oughton.

Spring 2020

"""
import os
import csv
import configparser
import pandas as pd

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')


def load_country_lut(path):
    """
    Load iso country list data.

    """
    output = []

    with open(path) as source:
        reader = csv.DictReader(source)
        for item in reader:
            output.append({
                'country': item['country'],
                'ISO_3digit': item['ISO_3digit'],
            })

    return output


def load_subscription_data(path, country, country_lut):
    """
    Load in itu cell phone subscription data.

    Parameters
    ----------
    path : string
        Location of itu data as .csv.
    country : string
        ISO3 digital country code.
    country_lut : list of dicts
        Lookup table containing country name to ISO3 digit code.

    Returns
    -------
    output :
        Time series data of cell phone subscriptions.

    """
    output = []
    unmatched = []

    years = [
        '2005',
        '2006',
        '2007',
        '2008',
        '2009',
        '2010',
        '2011',
        '2012',
        '2013',
        '2014',
        '2015',
        '2016',
        '2017',
    ]

    with open(path) as source:
        reader = csv.DictReader(source)
        for item in reader:

            #get 3 digital iso code from country name
            for country_code in country_lut:
                if item['country'] == country_code['country']:
                    iso_code = country_code['ISO_3digit']

            if not country == iso_code:
                continue

            keys = [k for k in item.keys()]

            for year in years:
                if year in keys:
                    try:
                        output.append({
                            'country': iso_code,
                            'year': int(year),
                            'penetration': float(item[year]),
                        })
                    except:
                        unmatched.append(item['country'])

            iso_code = None

    return output, unmatched


def forecast_linear(country, historical_data, start_point, end_point, horizon):
    """
    Forcasts subscription adoption rate.

    Parameters
    ----------
    historical_data : list of dicts
        Past penetration data.
    start_point : int
        Starting year of forecast period.
    end_point : int
        Final year of forecast period.
    horizon : int
        Number of years to use to estimate mean growth rate.

    """
    output = []

    for item in historical_data:
        output.append({
            'country': item['country'],
            'year': item['year'],
            'penetration': item['penetration'],
        })

    years = [item['year'] for item in historical_data]

    sorted_data = sorted(historical_data, key = lambda i: i['year'], reverse=False)

    year_0 = sorted(historical_data, key = lambda i: i['year'], reverse=True)[0]

    growth_rates = []

    for year in range((max(years)-horizon), max(years)):
        year_plus_1 = year + 1
        for item in sorted_data:
            if item['year'] == year:
                t0 = item['penetration']
            if item['year'] == year_plus_1:
                t1 = item['penetration']
        growth_rate = t1 - t0

        #exclude negative growth rates
        if growth_rate > 0:
            growth_rates.append(growth_rate)
        #exclude excessively high growth rates
        elif growth_rate < 8:
            growth_rates.append(growth_rate)
        else:
            pass

    mean_growth = sum(growth_rates) / len(growth_rates)

    for year in range(start_point, end_point + 1):
        if year == start_point:
            growth = (1 + (mean_growth/100))
            penetration = year_0['penetration'] * growth
        else:

            if penetration < 100:
                growth = (1 + (mean_growth/100))
            else:
                growth = (1 + ((mean_growth/2)/100))
            penetration = penetration * growth

        if year not in [item['year'] for item in output]:

            output.append({
                'country': country,
                'year': year,
                'penetration': round(penetration, 2),
            })

    return output


if __name__ == '__main__':

    all_subscription_data = []

    country_list = [
        'SEN',
        'UGA',
        'ETH',
        'BGD',
        'PER',
        'MWI',
        'ZAF'
    ]

    path = os.path.join(BASE_PATH, 'global_information.csv')
    country_lut = load_country_lut(path)

    for country in country_list:

        print('Working on {}'.format(country))

        path = os.path.join(DATA_RAW, 'itu', 'Mobile_cellular_2000-2018_Dec2019.csv')
        historical_data, unmatched = load_subscription_data(path, country, country_lut)

        forecast = forecast_linear(country, historical_data, 2018, 2030, 4)

        if len(all_subscription_data) == 0:
            all_subscription_data = forecast
        else:
            all_subscription_data = all_subscription_data + forecast

        forecast_df = pd.DataFrame(forecast)

        path = os.path.join(DATA_INTERMEDIATE, country, 'subscriptions')

        if not os.path.exists(path):
            os.mkdir(path)

        forecast_df.to_csv(os.path.join(path, 'subs_forecast.csv'), index=False)

    all_subscription_data = pd.DataFrame(all_subscription_data)

    path = os.path.join(BASE_PATH, '..', 'subscriptions', 'data_inputs')

    if not os.path.exists(path):
        os.mkdir(path)

    path = os.path.join(path, 'data_input.csv')
    all_subscription_data.to_csv(path, index=False)

    print('{} unmatched countries'.format(len(set(unmatched))))
