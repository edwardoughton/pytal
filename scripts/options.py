"""
Options consisting of scenarios and strategies.

Country parameters consist of those parameters which are specific
to each country.

Written by Ed Oughton

January 2020

#strategy is defined based on generation_core_backhaul_sharing_subsidy_spectrum_tax

"""
OPTIONS = {
    'technology_options': [
        {
            'scenario': 'S1_25_5_1',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
    ],
    'business_model_options': [
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
    ],
    'policy_options': [
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_low_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_low_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_low_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_high_baseline_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_high_baseline_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_high_baseline_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S1_25_5_1',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
        {
            'scenario': 'S2_100_20_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
        {
            'scenario': 'S3_400_80_20',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
    ]
}


COUNTRY_PARAMETERS = {

    'BOL': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 5,
            'subsidy_high': 20,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'COD': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'DZA': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2600,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'ETH': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'GBR': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2600,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'KEN': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
        'proportion_of_sites': 50,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'MEX': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
        'proportion_of_sites': 50,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'MWI': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },


    'PAK': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        # also GSMA, 2019 (same report as above)
        # smartphone pen was 10% in 2017, so assume 15% in 2020
        'smartphone_pen': 0.5,
        # Access Comm, Airtel, TNM
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'networks': 3,
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'proportion_of_sites': 50,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },


    'PER': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 700,
                    'bandwidth': 15,
                },
                {
                    'frequency': 2600,
                    'bandwidth': 20,
                },
            ],
            '5G': [
                {
                    'frequency': 3500,
                    'bandwidth': 50,
                },
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },


    'SEN': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.5,
        'networks': 3,
        'proportion_of_sites': 50,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'TZA': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'UGA': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2600,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    'ZAF': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 20,
            'medium': 10,
            'low': 5,
        },
        'smartphone_pen': 0.4,
        'networks': 3,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2600,
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
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },

    }
