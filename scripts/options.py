"""
Options consisting of scenarios and strategies.

Country parameters consist of those parameters which are specific
to each country.

Written by Ed Oughton

January 2020

#strategy is defined based on generation_core_backhaul_sharing

"""
OPTIONS = {
    'technology_options': [
        {
            'scenario': 'S1_30',
            'strategy': '4G_epc_microwave_baseline',
        },
        {
            'scenario': 'S2_50',
            'strategy': '4G_epc_microwave_baseline',
        },
        {
            'scenario': 'S3_200',
            'strategy': '4G_epc_microwave_baseline',
        },
        {
            'scenario': 'S1_30',
            'strategy': '4G_epc_fiber_baseline',
        },
        {
            'scenario': 'S2_50',
            'strategy': '4G_epc_fiber_baseline',
        },
        {
            'scenario': 'S3_200',
            'strategy': '4G_epc_fiber_baseline',
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_baseline',
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_baseline',
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_baseline',
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_sa_fiber_baseline',
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_sa_fiber_baseline',
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_sa_fiber_baseline',
        },
    ],
    'business_model_options': [
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_baseline',
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_baseline',
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_baseline',
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_passive',
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_passive',
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_passive',
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_active',
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_active',
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_active',
        },
    ],
}


COUNTRY_PARAMETERS = {

    'MWI': {
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
            },
        'financials': {
            'profit_margin': 20,
            'tax_baseline': 30,
            'tax_low': 10,
            },
        },
    'SEN': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 15,
            'medium': 5,
            'low': 2,
        },
        'smartphone_pen': 0.5,
        'networks': 3,
        'frequencies': {
            '4G': {
                '1_networks': [
                    {
                        'name': '',
                        'frequency': 800, #Actually 850 MHz but treating as 800 MHz
                        'bandwidth': 10 #Actually 5, treating as 10 for now
                    },
                    {
                        'name': '',
                        'frequency': 1800,
                        'bandwidth': 3
                    },
                    {
                        'name': '',
                        'frequency': 2500,
                        'bandwidth': 41
                    },
                ],
                '2_networks': [
                    {
                        'name': '',
                        'frequency': 800,
                        'bandwidth': 10 #Actually 5, treating as 10 for now
                    },
                    {
                        'name': '',
                        'frequency': 1800,
                        'bandwidth': 3
                    },
                ],
                '3_networks': [
                    {
                        'name': '',
                        'frequency': 800,
                        'bandwidth': 10 #Actually 5, treating as 10 for now
                    },
                ],
            },
            '5G': {
                '1_networks': [
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                ],
                '2_networks': [
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                ],
                '3_networks': [
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 10,
                    },
                ],
            }
        },
        'costs': {
            'spectrum_coverage_usd_mhz_pop': 0.5,
            'spectrum_capacity_usd_mhz_pop': 0.1,
            },
        'financials': {
            'profit_margin': 20,
            'tax_baseline': 30,
            'tax_low': 10,
            },
        },
    'PER': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 15,
            'medium': 5,
            'low': 2,
        },
        'smartphone_pen': 0.4,
        'networks': 4,
        'frequencies': {
            '4G': {
                '1_networks': [
                    {
                        'name': '',
                        'frequency': 800,
                        'bandwidth': 20,
                    },
                    {
                        'name': '',
                        'frequency': 1800,
                        'bandwidth': 20,
                    },
                    {
                        'name': '',
                        'frequency': 2100,
                        'bandwidth': 20,
                    },
                ],
                '2_networks': [
                    {
                        'name': '',
                        'frequency': 800,
                        'bandwidth': 20,
                    },
                    {
                        'name': '',
                        'frequency': 1800,
                        'bandwidth': 20,
                    },
                ],
                '3_networks': [
                    {
                        'name': '',
                        'frequency': 800,
                        'bandwidth': 20,
                    },
                ],
            },
            '5G': {
                '1_networks': [
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 20,
                    },
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 20,
                    },
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 20,
                    },
                ],
                '2_networks': [
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 20,
                    },
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 20,
                    },
                ],
                '3_networks': [
                    {
                        'name': '',
                        'frequency': 700,
                        'bandwidth': 20,
                    },
                ],
            }
        },
        'costs': {
            'spectrum_coverage_usd_mhz_pop': 0.5,
            'spectrum_capacity_usd_mhz_pop': 0.1,
            },
        'financials': {
            'profit_margin': 20,
            'tax_baseline': 30,
            'tax_low': 10,
            },
        },
    }
