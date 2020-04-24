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
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being testes in the model and is defined based
        on the type of technology generation, core and backhaul, and the level
        of sharing, subsidy, spectrum and tax.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    output : list of dicts
        Contains all output data.

    """
    interim = []

    strategy = option['strategy']
    available_for_cross_subsidy = 0

    for region in regions:

        # npv spectrum cost
        region['spectrum_cost'] = get_spectrum_costs(region, option['strategy'],
            global_parameters, country_parameters)

        #tax on investment
        region['tax'] = calculate_tax(region, strategy, country_parameters)

        #profit margin value calculated on all costs + taxes
        region['profit_margin'] = calculate_profit(region, country_parameters)

        region['total_cost'] = (
            region['network_cost'] +
            region['spectrum_cost'] +
            region['tax'] +
            region['profit_margin']
        )

        #avoid zero division
        if region['total_cost'] > 0 and region['smartphones_on_network'] > 0:
            region['cost_per_sp_user'] = region['total_cost'] / region['smartphones_on_network']
        else:
            region['cost_per_sp_user'] = 0

        #revenue cost ratio = expenses / revenue
        region['bcr'] = calculate_benefit_cost_ratio(region, country_parameters)

        region = allocate_available_excess(region)
        available_for_cross_subsidy += region['available_cross_subsidy']

        interim.append(region)

    interim = sorted(interim, key=lambda k: k['deficit'], reverse=False)

    output = []

    for region in interim:

        region, available_for_cross_subsidy = estimate_subsidies(
            region, available_for_cross_subsidy)

        output.append(region)

    return output


def allocate_available_excess(region):
    """
    Allocate available excess capital (if any).

    """
    difference = region['total_revenue'] - region['total_cost']

    if difference > 0:
        region['available_cross_subsidy'] = difference
        region['deficit'] = 0
    else:
        region['available_cross_subsidy'] = 0
        region['deficit'] = abs(difference)

    return region


def get_spectrum_costs(region, strategy, global_parameters, country_parameters):
    """
    Calculate spectrum costs.

    """
    population = int(round(region['population']))
    frequencies = country_parameters['frequencies']
    generation = strategy.split('_')[0]
    frequencies = frequencies[generation]

    spectrum_cost = strategy.split('_')[5]

    coverage_spectrum_cost = 'spectrum_coverage_baseline_usd_mhz_pop'
    capacity_spectrum_cost = 'spectrum_capacity_baseline_usd_mhz_pop'

    coverage_cost_usd_mhz_pop = country_parameters['financials'][coverage_spectrum_cost]
    capacity_cost_usd_mhz_pop = country_parameters['financials'][capacity_spectrum_cost]

    if spectrum_cost == 'low':
        coverage_cost_usd_mhz_pop = coverage_cost_usd_mhz_pop * 0.01
        capacity_cost_usd_mhz_pop = capacity_cost_usd_mhz_pop * 0.01

    if spectrum_cost == 'high':
        coverage_cost_usd_mhz_pop = coverage_cost_usd_mhz_pop * 2
        capacity_cost_usd_mhz_pop = capacity_cost_usd_mhz_pop * 2

    all_costs = []

    for frequency in frequencies:
        if frequency['frequency'] < 1000:
            cost = (
                coverage_cost_usd_mhz_pop * frequency['bandwidth'] *
                (population / global_parameters['networks'])
            )
            all_costs.append(cost)
        else:
            cost = (
                capacity_cost_usd_mhz_pop * frequency['bandwidth'] *
                (population / global_parameters['networks'])
            )
            all_costs.append(cost)

    return sum(all_costs)


def calculate_tax(region, strategy, country_parameters):
    """
    Calculate tax.

    """
    tax_rate = strategy.split('_')[6]
    tax_rate = 'tax_{}'.format(tax_rate)

    tax_rate = country_parameters['financials'][tax_rate]

    investment = region['network_cost']

    tax = investment * (tax_rate / 100)

    return tax


def calculate_profit(region, country_parameters):
    """
    Estimate npv profit.

    """
    investment = (
        region['network_cost'] +
        region['spectrum_cost'] +
        region['tax']
    )

    profit = investment * (country_parameters['financials']['profit_margin'] / 100)

    return profit


def estimate_subsidies(region, available_for_cross_subsidy):
    """
    Estimates either the contribution to cross-subsidies, or the
    quantity of subsidy required.

    Parameters
    ----------
    region : Dict
        Contains all variable for a single region.
    available_for_cross_subsidy : int
        The amount of capital available for cross-subsidization.

    Returns
    -------
    region : Dict
        Contains all variable for a single region.
    available_for_cross_subsidy : int
        The amount of capital available for cross-subsidization.

    """
    if region['deficit'] > 0:

        if available_for_cross_subsidy >= region['deficit']:
            region['used_cross_subsidy'] = region['deficit']
            available_for_cross_subsidy -= region['deficit']
        elif 0 < available_for_cross_subsidy < region['deficit']:
            region['used_cross_subsidy'] = available_for_cross_subsidy
            available_for_cross_subsidy = 0
        else:
            region['used_cross_subsidy'] = 0

    else:
        region['used_cross_subsidy'] = 0

    required_state_subsidy = (region['total_cost'] -
        (region['total_revenue'] + region['used_cross_subsidy']))

    if required_state_subsidy > 0:
        region['required_state_subsidy'] = required_state_subsidy
    else:
        region['required_state_subsidy'] = 0

    return region, available_for_cross_subsidy


def calculate_benefit_cost_ratio(region, country_parameters):
    """
    Calculate the benefit cost ratio.

    """
    cost = (
        region['network_cost'] +
        region['spectrum_cost'] +
        region['tax'] +
        region['profit_margin']
    )

    revenue = region['total_revenue']

    bcr = revenue / cost

    return bcr
