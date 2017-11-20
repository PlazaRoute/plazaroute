WEIGHTS = {
    'walking_duration':                  2,    # seconds
    'public_transport_duration':         1,    # seconds
    'number_of_legs':                    7*60  # number of legs in public transport route
}


def calculate_costs(legs):
    total_cost = 0
    for leg in legs:
        for key, value in leg.items():
            if key == 'duration':
                weight = WEIGHTS['walking_duration'] if leg['type'] == 'walking' \
                    else WEIGHTS['public_transport_duration']
            else:
                weight = WEIGHTS.get(key, None)
            if weight:
                total_cost += value * weight
    return total_cost
