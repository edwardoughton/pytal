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
    output = []

    strategy = option['strategy']

    regions = sorted(regions, key=lambda k: k['population_km2'], reverse=True)

    available_for_cross_subsidy = 0

    for region in regions:

        # npv spectrum cost
        region['spectrum_cost'] = get_spectrum_costs(region, option['strategy'], country_parameters)

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

        region, available_for_cross_subsidy = estimate_subsidies(region, available_for_cross_subsidy)
        print(available_for_cross_subsidy)
        #revenue cost ratio = expenses / revenue
        region['bcr'] = calculate_benefit_cost_ratio(region, country_parameters)

        output.append(region)

    return output


def get_spectrum_costs(region, strategy, country_parameters):
    """
    Calculate spectrum costs.

    """
    population = int(round(region['population']))
    frequencies = country_parameters['frequencies']
    generation = strategy.split('_')[0]
    frequencies = frequencies[generation]

    spectrum_cost = strategy.split('_')[5]

    coverage_spectrum_cost = 'spectrum_coverage_{}_usd_mhz_pop'.format(spectrum_cost)
    capacity_spectrum_cost = 'spectrum_capacity_{}_usd_mhz_pop'.format(spectrum_cost)

    all_costs = []

    for frequency in frequencies:
        if frequency['frequency'] < 1000:
            cost_usd_mhz_pop = country_parameters['financials'][coverage_spectrum_cost]
            cost = cost_usd_mhz_pop * frequency['bandwidth'] * population
            all_costs.append(cost)
        else:
            cost_usd_mhz_pop = country_parameters['financials'][capacity_spectrum_cost]
            cost = cost_usd_mhz_pop * frequency['bandwidth'] * population
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
    excess = region['total_revenue'] - region['total_cost']

    if excess > 0:
        available_for_cross_subsidy += excess
        region['available_cross_subsidy'] = excess
        region['used_cross_subsidy'] = 0
    else:
        if available_for_cross_subsidy >= abs(excess):
            region['available_cross_subsidy'] = 0
            region['used_cross_subsidy'] = abs(excess)
            available_for_cross_subsidy -= abs(excess)
        elif 0 < available_for_cross_subsidy < abs(excess):
            region['available_cross_subsidy'] = 0
            region['used_cross_subsidy'] = available_for_cross_subsidy
            available_for_cross_subsidy = 0
        else:
            region['available_cross_subsidy'] = 0
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

    revenue = region['total_revenue'] + region['used_cross_subsidy']

    bcr = revenue / cost

    return bcr
