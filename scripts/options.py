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
    #     {
    #         'scenario': 'S2_50',
    #         'strategy': '4G_epc_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 800, 'bandwidth': 10},
    #             {'frequency': 2600, 'bandwidth': 10},
    #         ],
    #     },
    #     {
    #         'scenario': 'S3_200',
    #         'strategy': '4G_epc_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 800, 'bandwidth': 10},
    #             {'frequency': 2600, 'bandwidth': 10},
    #         ],
    #     },
    #     {
    #         'scenario': 'S1_30',
    #         'strategy': '4G_epc_fiber_baseline',
    #         'frequencies': [
    #             {'frequency': 800, 'bandwidth': 10},
    #             {'frequency': 2600, 'bandwidth': 10},
    #         ],
    #     },
    #     {
    #         'scenario': 'S2_50',
    #         'strategy': '4G_epc_fiber_baseline',
    #         'frequencies': [
    #             {'frequency': 800, 'bandwidth': 10},
    #             {'frequency': 2600, 'bandwidth': 10},
    #         ],
    #     },
    #     {
    #         'scenario': 'S3_200',
    #         'strategy': '4G_epc_fiber_baseline',
    #         'frequencies': [
    #             {'frequency': 800, 'bandwidth': 10},
    #             {'frequency': 2600, 'bandwidth': 10},
    #         ],
    #     },
    #     {
    #         'scenario': 'S1_30',
    #         'strategy': '5G_nsa_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S2_50',
    #         'strategy': '5G_nsa_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S3_200',
    #         'strategy': '5G_nsa_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S1_30',
    #         'strategy': '5G_sa_fiber_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S2_50',
    #         'strategy': '5G_sa_fiber_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S3_200',
    #         'strategy': '5G_sa_fiber_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    # ],
    # 'business_model_options': [
    #     {
    #         'scenario': 'S1_30',
    #         'strategy': '5G_nsa_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S2_50',
    #         'strategy': '5G_nsa_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S3_200',
    #         'strategy': '5G_nsa_microwave_baseline',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S1_30',
    #         'strategy': '5G_nsa_microwave_passive',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S2_50',
    #         'strategy': '5G_nsa_microwave_passive',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S3_200',
    #         'strategy': '5G_nsa_microwave_passive',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S1_30',
    #         'strategy': '5G_nsa_microwave_active',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S2_50',
    #         'strategy': '5G_nsa_microwave_active',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    #     {
    #         'scenario': 'S3_200',
    #         'strategy': '5G_nsa_microwave_active',
    #         'frequencies': [
    #             {'frequency': 700, 'bandwidth': 10},
    #             {'frequency': 3500, 'bandwidth': 40},
    #         ],
    #     },
    ],
}


COUNTRY_PARAMETERS = {
    'MWI': {
        # Unique mobile subscribers = 30% (GSMA, 2019)
        # https://www.gsma.com/mobilefordevelopment/wp-content/uploads/2019/02/Digital-Identity-Country-Report.pdf
        'penetration': 0.3,
        # also GSMA, 2019 (same report as above)
        # smartphone pen was 10% in 2017, so assume 15% in 2020
        'smartphone_pen': 0.15,
        # Access Comm, Airtel, TNM
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'networks': 3,
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'frequencies': {
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
        'costs': {
            'spectrum_coverage_usd_mhz_pop': 0.5,
            'spectrum_capacity_usd_mhz_pop': 0.1,
        }
        },
    }
