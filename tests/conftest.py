from pytest import fixture


@fixture(scope='function')
def setup_region():
    return [{
    'GID_0': 'MWI',
    'GID_id': 'MWI.1.1.1_1',
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
        'overbooking_factor': 100,
        'return_period': 2,
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
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': 10,
                },
                {
                    'frequency': 3500,
                    'bandwidth': 50,
                },
                {
                    'frequency': 26000,
                    'bandwidth': 500,
                },
            ]
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
        # 2021,
        # 2022,
        # 2023,
        # 2024,
        # 2025,
        # 2026,
        # 2027,
        # 2028,
        # 2029,
        # 2030
    ]


@fixture(scope='function')
def setup_penetration_lut():
    return {
        2020: 50,
        # 2021: 75,
    }


@fixture(scope='function')
def setup_costs():
    return {
        #all costs in $USD
        'single_sector_antenna': 1500,
        'single_remote_radio_unit': 4000,
        'single_baseband_unit': 10000,
        'tower': 10000,
        'civil_materials': 5000,
        'transportation': 10000,
        'installation': 5000,
        'site_rental': 9600,
        'power_generator_battery_system': 5000,
        'high_speed_backhaul_hub': 15000,
        'router': 2000,
        'microwave_backhaul_small': 10000,
        'microwave_backhaul_medium': 20000,
        'microwave_backhaul_large': 40000,
        'fiber_backhaul_urban_m': 5,
        'fiber_backhaul_suburban_m': 5,
        'fiber_backhaul_rural_m': 5,
        'core_nodes_epc': 100000,
        'core_nodes_nsa': 150000,
        'core_nodes_sa': 200000,
        'core_edges': 20,
        'regional_nodes_epc': 100000,
        'regional_nodes_nsa': 150000,
        'regional_nodes_sa': 200000,
        'regional_edges': 10,
    }


@fixture(scope='function')
def setup_lookup():
    return {
        ('urban', 'macro', '800', '4G', '50'): [
            (0.01, 1),
            (0.02, 2),
            (0.05, 5),
            (0.15, 15),
            (2, 100)
        ],
        ('urban', 'macro', '1800', '4G', '50'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],

    }


@fixture(scope='function')
def setup_ci():
    return 50


@fixture(scope='function')
def setup_backhaul_lut():
    return {
        'MWI.1.1.1_1': 1000
    }


@fixture(scope='function')
def setup_core_lut():
    return {
        'core_edges': {
            'MWI.1.1.1_1': 1000
        },
        'core_nodes': {
            'MWI.1.1.1_1': 2
        },
        'regional_edges': {
            'MWI.1.1.1_1': 1000
        },
        'regional_nodes': {
            'MWI.1.1.1_1': 2
        },
    }
