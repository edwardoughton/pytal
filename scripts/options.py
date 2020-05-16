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
            'scenario': 'S1_25_10_2',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline',
        },
    ],
    'business_model_options': [
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_passive_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_active_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_shared_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_shared_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_shared_baseline_baseline_baseline',
        },
    ],
    'policy_options': [
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_baseline_baseline_low_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_baseline_baseline_high_baseline',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_low',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_baseline_baseline_baseline_high',
        },
    ],
    'mixed_options': [  #generation_core_backhaul_sharing_subsidy_spectrum_tax
        {
            'scenario': 'S1_25_10_2',
            'strategy': '4G_epc_microwave_shared_baseline_low_low',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '4G_epc_microwave_shared_baseline_low_low',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '4G_epc_microwave_shared_baseline_low_low',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '4G_epc_fiber_shared_baseline_low_low',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '4G_epc_fiber_shared_baseline_low_low',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '4G_epc_fiber_shared_baseline_low_low',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_nsa_microwave_shared_baseline_low_low',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_nsa_microwave_shared_baseline_low_low',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_nsa_microwave_shared_baseline_low_low',
        },
        {
            'scenario': 'S1_25_10_2',
            'strategy': '5G_sa_fiber_shared_baseline_low_low',
        },
        {
            'scenario': 'S2_200_50_5',
            'strategy': '5G_sa_fiber_shared_baseline_low_low',
        },
        {
            'scenario': 'S3_400_100_10',
            'strategy': '5G_sa_fiber_shared_baseline_low_low',
        },
    ]
}


COUNTRY_PARAMETERS = {
    'UGA': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 6,
            'medium': 3,
            'low': 2,
        },
        'networks': 2,
        'proportion_of_sites': 30,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 2600,
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
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.02,#0.0007,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.02,#0.0022,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 1,
            },
        },
    'MWI': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 6,
            'medium': 3,
            'low': 2,
        },
        # Access Comm, Airtel, TNM
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'networks': 2,
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'proportion_of_sites': 30,
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
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.02,#0.0007,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.02,#0.0022,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 1,
            },
        },
    'KEN': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 9,
            'medium': 7,
            'low': 2,
        },
        'networks': 3,
        'proportion_of_sites': 30,
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
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.1,#0.0051,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,#0.0049,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 2,
            },
        },
    'SEN': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 9,
            'medium': 7,
            'low': 2,
        },
        'smartphone_pen': 0.5,
        'networks': 3,
        'proportion_of_sites': 30,
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
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.05,#0.0051,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.05,#0.0049,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 2,
            },
        },
    'PAK': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 4,
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
        'proportion_of_sites': 30,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x5',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x5',
                },
                {
                    'frequency': 2600,
                    'bandwidth': '1x20',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x20',
                },
            ]
        },
        'financials': {
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.05,#0.0016,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.05,#0.0003,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 4,
            },
        },
    'ALB': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 9,
            'medium': 7,
            'low': 5,
        },
        'networks': 3,
        'proportion_of_sites': 30,
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
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.1,#0.0267,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,#0.0109,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 4,
            },
        },
    'PER': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 12,
            'medium': 10,
            'low': 7,
        },
        'networks': 3,
        'proportion_of_sites': 30,
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
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.1,#0.0164,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,#0.0041,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 4,
            },
        },
    'MEX': {
        'luminosity': {
            'high': 3,
            'medium': 1,
        },
        'arpu': {
            'high': 12,
            'medium': 10,
            'low': 7,
        },
        'networks': 3,
        'proportion_of_sites': 30,
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
            'wacc': 15,
            'profit_margin': 10,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.12,#0.0225,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.12,#0.0026,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'ops_and_acquisition_per_subscriber': 6,
            },
        },
    }
