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

    strategy = option['strategy']

    subsidy = option['strategy'].split('_')[4]

    for region in regions:

        # npv spectrum cost
        region['total_spectrum_cost'] = get_spectrum_costs(region, option['strategy'], country_parameters)

        #tax on investment
        region['total_tax'] = calculate_tax(region, strategy, country_parameters)

        #profit margin value calculated on all costs + taxes
        region['total_profit'] = calculate_profit(region, country_parameters)

        #revenue cost ratio = expenses / revenue
        region['bcr'] = calculate_benefit_cost_ratio(region, country_parameters)

        if not subsidy == 'baseline':
            subsidy_level = 'subsidy_{}'.format(subsidy)
            region['total_network_cost'] = region['total_network_cost'] * (1 - (country_parameters['financials'][subsidy_level] / 100))

        region['total_cost'] = (
            region['total_network_cost'] +
            region['total_spectrum_cost'] +
            region['total_tax'] +
            region['total_profit']
        )

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

    investment = (
        region['total_network_cost'] +
        region['total_spectrum_cost']
    )

    tax = investment * (tax_rate / 100)

    return tax


def calculate_profit(region, country_parameters):
    """
    Estimate npv profit.

    """
    investment = (
        region['total_network_cost'] +
        region['total_spectrum_cost'] +
        region['total_tax']
    )

    profit = investment * (country_parameters['financials']['profit_margin'] / 100)

    return profit


def calculate_benefit_cost_ratio(region, country_parameters):
    """

    """
    cost = (
        region['total_network_cost'] +
        region['total_spectrum_cost'] +
        region['total_tax'] +
        region['total_profit']
    )

    revenue = region['total_revenue']

    bcr = revenue / cost

    return bcr
