

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def is_enemy_fleet_incoming(state):
    # Store the list of planets in a variable to prevent this algorithm from being too inefficient
    my_planets = state.my_planets()
    return any(fleet.destination_planet in my_planets for fleet in state.enemy_fleets())