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
            'scenario': 'S1_25_10_5',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
    ],
    'business_model_options': [
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_shared_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_shared_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_shared_baseline_baseline_baseline',
        },
    ],
    'policy_options': [
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S1_25_10_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
        {
            'scenario': 'S2_200_50_25',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
        {
            'scenario': 'S3_400_100_50',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
    ]
}


COUNTRY_PARAMETERS = {
    'ALB': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 10,
            'medium': 7,
            'low': 5,
        },
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 5,
            'subsidy_high': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0267,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0109,
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
            'high': 12,
            'medium': 9,
            'low': 5,
        },
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0051,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0049,
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
            'high': 10,
            'medium': 8,
            'low': 4,
        },
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x20',
                },
                {
                    'frequency': 850,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1700,
                    'bandwidth': '2x20',
                },
                {
                    'frequency': 1900,
                    'bandwidth': '2x20',
                },
            ],
            '5G': [
                {
                    'frequency': 2500,
                    'bandwidth': '2x20',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0225,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0026,
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
            'high': 10,
            'medium': 3,
            'low': 1,
        },
        # Access Comm, Airtel, TNM
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'networks': 2,
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0007,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0022,
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
            'high': 10,
            'medium': 2,
            'low': 1,
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
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0016,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0003,
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
            'high': 15,
            'medium': 12,
            'low': 5,
        },
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x30',
                },
                {
                    'frequency': 2600,
                    'bandwidth': '2x20',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x15',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0164,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0041,
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
            'high': 10,
            'medium': 8,
            'low': 5,
        },
        'smartphone_pen': 0.5,
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0051,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0049,
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
            'high': 10,
            'medium': 3,
            'low': 2,
        },
        'networks': 2,
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.0007,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.0022,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },
    }
