"""
Options consisting of scenarios and strategies.

Country parameters consist of those parameters which are specific
to each country.

Written by Ed Oughton

January 2020

#strategy is defined based on generation_core_backhaul_sharing_networks_spectrum_tax

generation: technology generation, so 3G or 4G
core: type of core data transport network, eg. evolved packet core (4G)
backhaul: type of backhaul, so fiber or microwave
sharing: the type of infrastructure sharing, active, passive etc..
network: relates to the number of networks, as defined in country parameters
spectrum: type of spectrum strategy, so baseline, high or low
tax: type of taxation strategy, so baseline, high or low

"""
def generate_tech_options():
    """
    Generate technology strategy options.

    """
    output = []

    scenarios = ['S1_25_10_2', 'S2_200_50_5', 'S3_400_100_10']
    generation_core_types = ['4G_epc', '5G_nsa', '5G_sa']
    backhaul_types = ['microwave', 'fiber']
    sharing_types = ['baseline']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:

                    if generation_core_type == '5G_nsa' and backhaul == 'fiber':
                        continue

                    if generation_core_type == '5G_sa' and backhaul == 'microwave':
                        continue

                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
                                    )
                                    output.append({
                                        'scenario': scenario,
                                        'strategy': strategy
                                    })

    return output


def generate_business_model_options():
    """
    Generate business model strategy options.

    """
    output = []

    scenarios = ['S1_25_10_2', 'S2_200_50_5', 'S3_400_100_10']
    generation_core_types = ['4G_epc','5G_nsa', '5G_sa']
    backhaul_types = ['microwave', 'fiber']
    sharing_types = ['baseline', 'passive', 'active', 'shared']
    networks_types = ['baseline']
    spectrum_types = ['baseline']
    tax_types = ['baseline']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:

                    if generation_core_type == '5G_nsa' and backhaul == 'fiber':
                        continue

                    if generation_core_type == '5G_sa' and backhaul == 'microwave':
                        continue

                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
                                    )
                                    output.append({
                                        'scenario': scenario,
                                        'strategy': strategy
                                    })

    return output


def generate_policy_options():
    """
    Generate policy strategy options.

    """
    output = []

    scenarios = [
        'S1_25_10_2',
        'S2_200_50_5',
        'S3_400_100_10'
        ]
    generation_core_types = [
        '4G_epc',
        '5G_nsa',
        '5G_sa'
        ]
    backhaul_types = [
        'microwave',
        'fiber'
        ]
    sharing_types = ['baseline']
    networks_types = ['baseline']
    spectrum_types = ['baseline', 'low', 'high']
    tax_types = [
        'baseline',
        'low',
        'high'
        ]

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:

                    if generation_core_type == '5G_nsa' and backhaul == 'fiber':
                        continue

                    if generation_core_type == '5G_sa' and backhaul == 'microwave':
                        continue

                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
                                    )
                                    output.append({
                                        'scenario': scenario,
                                        'strategy': strategy
                                    })

    return output


def generate_mixed_options():
    """
    Generate policy strategy options.

    """
    output = []

    scenarios = ['S1_25_10_2', 'S2_200_50_5', 'S3_400_100_10']
    generation_core_types = ['4G_epc','5G_nsa', '5G_sa']
    backhaul_types = ['microwave', 'fiber']
    sharing_types = ['shared']
    networks_types = ['baseline']
    spectrum_types = ['low']
    tax_types = ['low']

    for scenario in scenarios:
        for generation_core_type in generation_core_types:
                for backhaul in backhaul_types:

                    if generation_core_type == '5G_nsa' and backhaul == 'fiber':
                        continue

                    if generation_core_type == '5G_sa' and backhaul == 'microwave':
                        continue

                    for sharing in sharing_types:
                        for network in networks_types:
                            for spectrum in spectrum_types:
                                for tax in tax_types:
                                    strategy = '{}_{}_{}_{}_{}_{}'.format(
                                        generation_core_type,
                                        backhaul,
                                        sharing,
                                        network,
                                        spectrum,
                                        tax
                                    )
                                    output.append({
                                        'scenario': scenario,
                                        'strategy': strategy
                                    })

    return output


OPTIONS = {
    'technology_options': generate_tech_options(),
    'business_model_options': generate_business_model_options(),
    'policy_options': generate_policy_options(),
    'mixed_options': generate_mixed_options(),
}


COUNTRY_PARAMETERS = {
    'MWI': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 3.5,
            'medium': 2.5,
            'low': 1,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'shared_urban': 3,
            'shared_suburban': 3,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.02,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.01,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    'UGA': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 3.5,
            'medium': 2.5,
            'low': 1,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'shared_urban': 3,
            'shared_suburban': 3,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.02,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.01,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    'SEN': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 8,
            'medium': 5,
            'low': 2,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'shared_urban': 3,
            'shared_suburban': 3,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.15,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.08,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    'KEN': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 8,
            'medium': 5,
            'low': 2,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'shared_urban': 3,
            'shared_suburban': 3,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.15,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.08,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    'PAK': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 4,
            'medium': 2,
            'low': 1,
        },
        'networks': {
            'baseline_urban': 4,
            'baseline_suburban': 4,
            'baseline_rural': 4,
            'shared_urban': 4,
            'shared_suburban': 4,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.05,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.025,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    'ALB': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 8,
            'medium': 7,
            'low': 4,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'shared_urban': 3,
            'shared_suburban': 3,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.4,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    'PER': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 11,
            'medium': 10,
            'low': 5,
        },
        'networks': {
            'baseline_urban': 4,
            'baseline_suburban': 4,
            'baseline_rural': 4,
            'shared_urban': 4,
            'shared_suburban': 4,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.2,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    'MEX': {
        'luminosity': {
            'high': 20,
            'medium': 15,
        },
        'arpu': {
            'high': 11,
            'medium': 10,
            'low': 5,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'shared_urban': 3,
            'shared_suburban': 3,
            'shared_rural': 1,
        },
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
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.2,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_cost_low': 25,
            'spectrum_cost_high': 100,
            'tax_low': 10,
            'tax_baseline': 30,
            'tax_high': 40,
            'administration_percentage_of_network_cost': 20,
            },
        },
    }
