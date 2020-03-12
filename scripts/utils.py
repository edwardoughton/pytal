"""
Utils contains general functions required throughout the model.

Written by Ed Oughton.

Spring 2020.

"""

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


# def discount_revenue(revenue, timestep, global_parameters):
#     """
#     Discount revenue based on return period.

#     192,744 = 23,773 / (1 + 0.05) ** (0:9)

#     Parameters
#     ----------
#     revenue : float
#         Financial revenue.
#     global_parameters : dict
#         All global model parameters.

#     Returns
#     -------
#     discounted_revenue : float
#         The discounted revenue over the desired time period.

#     """
#     return_period = global_parameters['return_period']
#     discount_rate = global_parameters['discount_rate'] / 100

#     revenue_over_time_period = []

#     for i in range(0, return_period):
#         revenue_over_time_period.append(
#             revenue / (1 + discount_rate) ** i
#         )

#     discounted_revenue = sum(revenue_over_time_period)

#     return discounted_revenue


def discount_capex_and_opex(capex, global_parameters):
    """
    Discount costs based on return period.

    Parameters
    ----------
    cost : float
        Financial cost.
    global_parameters : dict
        All global model parameters.

    Returns
    -------
    discounted_cost : float
        The discounted cost over the desired time period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100

    costs_over_time_period = []

    costs_over_time_period.append(capex)

    opex = round(capex * (global_parameters['opex_percentage_of_capex'] / 100))

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = sum(costs_over_time_period)

    return discounted_cost


def discount_opex(opex, global_parameters):
    """
    Discount opex based on return period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100

    costs_over_time_period = []

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = sum(costs_over_time_period)

    return discounted_cost
