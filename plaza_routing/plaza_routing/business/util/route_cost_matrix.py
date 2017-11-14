WEIGHTS = {
    'time':             2,  # walking time
    'duration':         2,  # travel duration of public transport connection
    'ascend':           0.75,
    'descend':          0.5,
    'number_of_legs':   1
}  # TODO: deal with different value ranges (ex. number_of_legs and time)


def calculate_costs(legs):
    total_cost = 0
    for leg in legs:
        for key, weight in WEIGHTS.items():
            total_cost += leg.get(key, 0) * weight
    return total_cost
