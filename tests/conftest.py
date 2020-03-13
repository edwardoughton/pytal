from pytest import fixture


@fixture(scope='function')
def setup_region():
    return [{
    'GID_0': 'MWI',
    'GID_3': 'MWI.1.1.1_1',
    'median_luminosity': 20.5,
    'sum_luminosity': 41.0,
    'mean_luminosity_km2': 26.736407691655717,
    'population': 10000,
    'area_km2': 2,
    'population_km2': 5000,
    'decile': 100,
    'geotype': 'urban'
    }]


@fixture(scope='function')
def setup_option():
    return {
        'scenario': 'S1_30',
        'strategy': '4G_epc_microwave_baseline'
    }


@fixture(scope='function')
def setup_global_parameters():
    return {
        'overbooking_factor': 50,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        'confidence': [1, 10, 50]
    }


@fixture(scope='function')
def setup_country_parameters():
    return {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 15,
            'medium': 5,
            'low': 2,
        },
        # also GSMA, 2019 (same report as above)
        # smartphone pen was 10% in 2017, so assume 15% in 2020
        'smartphone_pen': 0.5,
        # Access Comm, Airtel, TNM
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'networks': 3,
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'frequencies': {
            '4G': {
                    '1_networks': [
                        {
                            'name': 'Access Comm',
                            'frequency': 800, #Actually 850 MHz but treating as 800 MHz
                            'bandwidth': 10 #Actually 5, treating as 10 for now
                        },
                        {
                            'name': 'Airtel',
                            'frequency': 1800,
                            'bandwidth': 3
                        },
                        {
                            'name': 'TNM',
                            'frequency': 2500,
                            'bandwidth': 41
                        },
                    ],
                '2_networks': [
                    {
                        'name': 'Access Comm',
                        'frequency': 800,
                        'bandwidth': 10 #Actually 5, treating as 10 for now
                    },
                    {
                        'name': 'Airtel',
                        'frequency': 1800,
                        'bandwidth': 3
                    },
                ],
                '3_networks': [
                    {
                        'name': 'Access Comm',
                        'frequency': 800,
                        'bandwidth': 10 #Actually 5, treating as 10 for now
                    },
                ],
            },
            '5G': {
                '1_networks': [
                    {
                        'name': 'Access Comm',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                    {
                        'name': 'Airtel',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                    {
                        'name': 'TNM',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                ],
                '2_networks': [
                    {
                        'name': 'Access Comm',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                    {
                        'name': 'Airtel',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                ],
                '3_networks': [
                    {
                        'name': 'Access Comm',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                ],
            }
        },
        'costs': {
            'spectrum_coverage_usd_mhz_pop': 0.5,
            'spectrum_capacity_usd_mhz_pop': 0.1,
            }
        }


@fixture(scope='function')
def setup_timesteps():
    return [
        2020,
        2021,
        2022,
        2023,
        2024,
        2025,
        2026,
        2027,
        2028,
        2029,
        2030
    ]


@fixture(scope='function')
def setup_penetration_lut():
    return {
        2005: 3.34,
        2006: 4.78,
        2007: 7.88,
        2008: 10.98,
        2009: 17.59,
        2010: 21.44,
        2011: 26.41,
        2012: 30.18,
        2013: 33.4,
        2014: 34.58,
        2015: 39.22,
        2016: 41.72,
        2017: 43.99,
        2018: 45.15,
        2019: 46.35,
        2020: 47.58,
        2021: 48.84,
        2022: 50.13,
        2023: 51.46,
        2024: 52.82,
        2025: 54.22,
        2026: 55.65,
        2027: 57.13,
        2028: 58.64,
        2029: 60.19,
        2030: 61.78
    }
