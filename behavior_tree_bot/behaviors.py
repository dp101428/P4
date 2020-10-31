import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def defend_planets(state):
    #Finds if any planet has more enemies incoming than it can hold off
    # Store the list of planets in a variable to prevent this algorithm from being too inefficient
    my_planets = dict.fromkeys(state.my_planets())
    #Get the IDs separately to allow "in" to work
    #Doing this here rather than within the other list comprehension for efficiency purposes
    my_planets_IDs = [planet.ID for planet in my_planets]
    #Get list of enemy fleets incoming to them
    attacking_fleets = [fleet.destination_planet in my_planets_IDs for fleet in state.enemy_fleets()]
    #Establish the list of planets that need help
    doomed_planets = {}
    #Go through each planet
    for planet in my_planets:
        #Get what is attacking it
        my_planets[planet] = [fleet.destination_planet == planet.ID for fleet in attacking_fleets]
        #Fleets can only go to one place, so remove the excess for efficency
        attacking_fleets = [fleet not in my_planets[planet] for fleet in attacking_fleets]
        #If this planet is being attacked, check to see if it can hold out
        if len(my_planets[planet]) != 0:
            my_planets[planet].sort(key = lambda f: f.turns_remaining)
            #Establish the defending forces regardless of time
            defenders = planet.num_ships
            #Establish how much time has passed
            turns_in_future = 0
            #Check how it holds up per enemy fleet
            for fleet in my_planets[planet]:
                #Find how many more ships will be made before the next fleet arrives
                defenders += (fleet.turns_remaining - turns_in_future) * planet.growth_rate
                #Update the time
                turns_in_future = fleet.turns_remaining
                #Subtract out the casualties from the new fleet
                defenders -= fleet.num_ships
                #If the planet will be overwhelmed, add it to the list to reinforce
                if defenders <= 0:
                    # If there's no necessary reinforcing, start the list
                    if planet not in doomed_planets:
                        doomed_planets[planet] = [(-defenders + 1, turns_in_future)]
                    # Otherwise, add it to the list
                    else:
                        #Check first if another fleet is arriving simultaniously
                        if doomed_planets[planet][-1][1] == turns_in_future:
                            doomed_planets[planet][-1][0] = -defenders + 1
                        #Otherwise just add the difference between this and the last attack
                        else:
                            doomed_planets[planet].append(((-defenders) - doomed_planets[planet][-1][0] + 1, turns_in_future))
                    
        #Use helper function that I will totally write soon to handle the planets that need help
        #fulfil_fleets(doomed_planets, doomed_planets.keys())

    
    #for fleet in attacking_fleets:
    #    my_planets[state.planets[fleet.destination_planet]] = fleet
    #return any(fleet.destination_planet in my_planets for fleet in state.enemy_fleets())