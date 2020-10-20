"""
Estimate demand

Written by Ed Oughton.

Winter 2020

"""

def estimate_demand(regions, option, global_parameters,
    country_parameters, timesteps, penetration_lut, smartphone_lut):
    """
    Estimate demand metrics including:
        - Total number of basic phone and smartphone users
        - Total data demand (in Mbps per square kilometer)
        - Total revenue (net present value over the assessment period in USD)

    Parameters
    ----------
    regions : list of dicts
        Data for all regions (one dict per region).
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being tested in the model and is defined based
        on the type of technology generation, core and backhaul, and the
        strategy for infrastructure sharing, the number of networks in each
        geotype, spectrum and taxation.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.
    timesteps : list
        All years for the assessment period.
    penetration_lut : list of dicts
        Contains annual cell phone penetration values.
    smartphone_lut : list of dicts
        Contains annual penetration values for smartphones.

    Returns
    -------
    regions : list of dicts
        Data for all regions (one dict per region).

    """
    output = []
    annual_output = []

    # generation_core_backhaul_sharing_networks_spectrum_tax
    network_strategy = option['strategy'].split('_')[4]

    for region in regions:

        if not region['area_km2'] > 0:
            continue

        geotype = region['geotype'].split(' ')[0]

        net_handle = network_strategy + '_' + geotype
        networks = country_parameters['networks'][net_handle]

        if geotype == 'suburban':
            #smartphone lut only has urban-rural split, hence no suburban
            geotype_sps = 'urban'
        else:
            geotype_sps = geotype

        revenue = []
        demand_mbps_km2 = []

        scenario_per_user_capacity = get_per_user_capacity(
            region['geotype'], option)

        for timestep in timesteps:

            region['arpu_discounted_monthly'] = estimate_arpu(
                region,
                timestep,
                global_parameters,
                country_parameters
            )

            region['penetration'] = penetration_lut[timestep]

            #cell_penetration : float
            #Number of cell phones per member of the population.
            region['population_with_phones'] = (
                region['population'] * (region['penetration'] / 100))

            #phones : int
            #Total number of phones on the network being modeled.
            region['phones_on_network'] = (
                region['population_with_phones'] /
                networks)

            #get phone density
            region['phone_density_on_network_km2'] = (
                region['phones_on_network'] / region['area_km2']
            )

            #add regional smartphone penetration
            region['smartphone_penetration'] = smartphone_lut[geotype_sps][timestep]

            #phones : int
            #Total number of smartphones on the network being modeled.
            region['smartphones_on_network'] = (
                region['phones_on_network'] *
                (region['smartphone_penetration'] / 100)
            )

            #get smartphone density
            region['sp_density_on_network_km2'] = (
                region['smartphones_on_network'] / region['area_km2']
            )

            # demand_mbps_km2 : float
            # Total demand in mbps / km^2.
            demand_mbps_km2.append(
                (region['smartphones_on_network'] *
                scenario_per_user_capacity / #User demand in Mbps
                global_parameters['overbooking_factor'] /
                region['area_km2']
                ))

            annual_revenue = (
                region['arpu_discounted_monthly'] *
                region['phones_on_network'] *
                12
            )

            revenue.append(annual_revenue)

            annual_output.append({
                'GID_0': region['GID_0'],
                'GID_id': region['GID_id'],
                'scenario': option['scenario'],
                'strategy': option['strategy'],
                'confidence': global_parameters['confidence'][0],
                'year': timestep,
                'population': region['population'],
                'area_km2': region['area_km2'],
                'population_km2': region['population_km2'],
                'geotype': region['geotype'],
                'arpu_discounted_monthly': region['arpu_discounted_monthly'],
                'penetration': region['penetration'],
                'population_with_phones': region['population_with_phones'],
                'phones_on_network': region['phones_on_network'],
                'smartphone_penetration': region['smartphone_penetration'],
                'smartphones_on_network': region['smartphones_on_network'],
                'revenue': annual_revenue,
            })

        region['demand_mbps_km2'] = max(demand_mbps_km2)
        region['total_mno_revenue'] = round(sum(revenue))
        region['revenue_km2'] = round(sum(revenue) / region['area_km2'])

        output.append(region)

    return output, annual_output


def get_per_user_capacity(geotype, option):
    """
    Function to return the target per user capacity by scenario,
    from the scenario string.

    Parameters
    ----------
    geotype : string
        Settlement patterns, such as urban, suburban or rural.
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being tested in the model and is defined based
        on the type of technology generation, core and backhaul, and the
        strategy for infrastructure sharing, the number of networks in each
        geotype, spectrum and taxation.

    Returns
    -------
    per_user_capacity : int
        The targetted per user capacity in Mbps.

    """
    if geotype.split(' ')[0] == 'urban':

        return int(option['scenario'].split('_')[1])

    elif geotype.split(' ')[0] == 'suburban':

        return int(option['scenario'].split('_')[2])

    elif geotype.split(' ')[0] == 'rural':

        return int(option['scenario'].split('_')[3])

    else:
        return 'Did not recognise geotype'


def estimate_arpu(region, timestep, global_parameters, country_parameters):
    """
    Allocate consumption category given a specific luminosity.

    Parameters
    ----------
    region : dicts
        Data for a single region.
    timestep : int
        Time period (year) to discount against.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    discounted_arpu : float
        The discounted Average Revenue Per User (ARPU) over the time period.

    """
    timestep = timestep - 2020

    if region['mean_luminosity_km2'] > country_parameters['luminosity']['high']:
        arpu = country_parameters['arpu']['high']
        return discount_arpu(arpu, timestep, global_parameters)

    elif region['mean_luminosity_km2'] > country_parameters['luminosity']['medium']:
        arpu = country_parameters['arpu']['medium']
        return discount_arpu(arpu, timestep, global_parameters)

    else:
        arpu = country_parameters['arpu']['low']
        return discount_arpu(arpu, timestep, global_parameters)


def discount_arpu(arpu, timestep, global_parameters):
    """
    Discount arpu based on return period.

    192,744 = 23,773 / (1 + 0.05) ** (0:9)

    Parameters
    ----------
    arpu : float
        Average revenue per user.
    timestep : int
        Time period (year) to discount against.
    global_parameters : dict
        All global model parameters.

    Returns
    -------
    discounted_arpu : float
        The discounted revenue over the desired time period.

    """
    discount_rate = global_parameters['discount_rate'] / 100

    discounted_arpu = arpu / (1 + discount_rate) ** timestep

    return discounted_arpu
