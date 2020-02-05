"""
Options consisting of scenarios and strategies.

Written by Ed Oughton

January 2020

#strategy is generation_core_backhaul_sharing

"""
OPTIONS = {
    'technology_options': [
        {
            'scenario': 'S1_30',
            'strategy': '4G_epc_microwave_baseline',
            'frequencies': [
                {'frequency': 800, 'bandwidth': 10},
                {'frequency': 2600, 'bandwidth': 10},
            ],
        },
        {
            'scenario': 'S2_50',
            'strategy': '4G_epc_microwave_baseline',
            'frequencies': [
                {'frequency': 800, 'bandwidth': 10},
                {'frequency': 2600, 'bandwidth': 10},
            ],
        },
        {
            'scenario': 'S3_200',
            'strategy': '4G_epc_microwave_baseline',
            'frequencies': [
                {'frequency': 800, 'bandwidth': 10},
                {'frequency': 2600, 'bandwidth': 10},
            ],
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_sa_fiber_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_sa_fiber_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_sa_fiber_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
    ],
    'business_model_options': [
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_baseline',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_passive',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_passive',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_passive',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S1_30',
            'strategy': '5G_nsa_microwave_active',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S2_50',
            'strategy': '5G_nsa_microwave_active',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
        {
            'scenario': 'S3_200',
            'strategy': '5G_nsa_microwave_active',
            'frequencies': [
                {'frequency': 700, 'bandwidth': 10},
                {'frequency': 3500, 'bandwidth': 40},
            ],
        },
    ],
}
