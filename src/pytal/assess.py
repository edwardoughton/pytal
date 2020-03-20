"""
Assessment Module

Written by Ed Oughton.

Winter 2020

"""

def assess(country, regions, option, global_parameters, country_parameters):
    """
    For each region, assess the viability level.

    Parameters
    ----------
    country : dict
        Country information.
    regions : dataframe
        Geopandas dataframe of all regions.
    option : dict
        Contains the scenario, strategy, and frequencies
        with bandwidths.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    output : list of dicts
        Contains all output data.

    """
    output = []

    generation, core, backhaul, sharing = get_strategy_options(option['strategy'])

    for region in regions:

        # npv spectrum cost
        region['total_spectrum_cost'] = get_spectrum_costs(region, generation, country_parameters)

        #profit = revenue - network cost + spectrum cost
        region['total_profit'] = calculate_profit(region, country_parameters)

        #tax only on profits
        region['total_tax'] = calculate_tax(region, country_parameters)

        #revenue cost ratio = expenses / revenue
        region['bcr'] = calculate_benefit_cost_ratio(region, country_parameters)

        region['per_phone_user_cost'] = calculate_phone_user_cost(region, country_parameters)

        region['per_smartphone_user_cost'] = calculate_smartphone_user_cost(region, country_parameters)

        output.append(region)

    return output


def get_strategy_options(strategy):

    #strategy is 'generation_core_backhaul_sharing'
    generation = strategy.split('_')[0]
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    return generation, core, backhaul, sharing


def get_spectrum_costs(region, generation, country_parameters):
    """
    Calculate spectrum costs.

    """
    population = int(round(region['population']))
    frequencies = country_parameters['frequencies']
    frequencies = frequencies[generation]
    networks = country_parameters['networks']

    for frequency in frequencies:
        if frequency['frequency'] < 1000:
            cost_usd_mhz_pop = country_parameters['costs']['spectrum_coverage_usd_mhz_pop']
        else:
            cost_usd_mhz_pop = country_parameters['costs']['spectrum_capacity_usd_mhz_pop']

    cost = cost_usd_mhz_pop * frequency['bandwidth'] * population

    return cost


def calculate_profit(region, country_parameters):
    """
    Estimate npv profit.

    """
    revenue = region['total_revenue']

    cost = region['total_network_cost'] + region['total_spectrum_cost']

    profit = revenue - cost

    return profit


def calculate_tax(region, country_parameters):
    """

    """
    tax_rate = country_parameters['financials']['tax_baseline']

    tax = region['total_profit'] * (tax_rate / 100)

    return tax


def calculate_benefit_cost_ratio(region, country_parameters):
    """

    """
    cost = (
        region['total_network_cost'] +
        region['total_spectrum_cost'] +
        region['total_tax']
    )

    revenue = region['total_revenue']

    bcr = revenue - cost

    return bcr


def calculate_phone_user_cost(region, country_parameters):
    """

    """
    cost = (
        region['total_network_cost'] +
        region['total_spectrum_cost'] +
        region['total_profit']
    )

    if region['phones_on_network'] > 0:

        cost_per_user = cost / region['phones_on_network']

    else:

        cost_per_user = 0

    return cost_per_user


def calculate_smartphone_user_cost(region, country_parameters):
    """

    """
    cost = (
        region['total_network_cost'] +
        region['total_spectrum_cost'] +
        region['total_profit']
    )

    if region['smartphones_on_network'] > 0:

        cost_per_smartphone_user = cost / region['smartphones_on_network']

    else:

        cost_per_smartphone_user = 0

    return cost_per_smartphone_user
