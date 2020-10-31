import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging


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
        #To save time, stop looking at planets if there are no longer any fleets coming to them
        if len(attacking_fleets) == 0:
            break
    #If we didn't find anything to care about, just return
    if len(doomed_planets) == 0:
        return True
    #Use helper function that I will totally write soon to handle the planets that need help
    return fulfil_fleets(state, doomed_planets)

    
#Helper function for sending fleets to places that need them
#Argument is a list of tuples containing destination, required ships, time
#If time is irrelevant, pass 0 for it
def fulfil_fleets(state, requirements):
    #Break the input into multiple tuples, might be useful
    destinations, required_ships, eta = zip(*requirements)
    #Only send fleets from planets that aren't destinations
    my_planets = state.my_planets()
    usable_planets = [planet not in destinations for planet in my_planets]
    #Keep track of whether we managed to satisfy everything
    satisfied = True
    #Start fulfilling all the things
    for assignment in requirements:
        #Not yet fulfilled
        fulfilled = False
        #Go through the usable planets
        for planet in usable_planets:
            #Check range if it matters
            if assignment[2] != 0 and state.distance(planet.ID, assignment[0].ID) > assignment[2]:
                #If distance is bad, go to the next planet
                continue
            #Otherwise, check if we can send enough ships
            if planet.num_ships > assignment[1]:
                #If so, do it
                issue_order(state, planet.ID, assignment[0].ID, assignment[1])
                #record that it was fulfilled
                fulfilled = True
                #Go to the next assignment
                break
        #Check if we managed to fulfil it, if not we need to return false later
        if not fulfilled:
            satisfied = False
            #Log the failure
            logging.debug("Failed to fulfil " + assignment[1] + " ships at " + assignment[0].ID + " at time " + assignemnt[2] + ".")
    return satisfied




def spread_to_highest_producer(state):
    #print("where are we crashing")
    #neutral planets only holds planets that we arent already going to
    neutral_planets = [planet for planet in state.neutral_planets() 
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.growth_rate) #they are sorted for growth rate
    neutral_planets.reverse()
    #my planets only contains allied planets that do not have enemy ships heading towards them 
    my_planets = [planet for planet in state.my_planets()
                  if not any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]
    my_planets.sort(key=lambda p: p.num_ships)
    #sorted by num ships and reverse so highest first
    my_planets.reverse()
    

    for planet in neutral_planets:
        for me in my_planets:
            required_ships = planet.num_ships + 1
            if me.num_ships > required_ships:
                return issue_order(state, me.ID, planet.ID, required_ships)
            else:
                #if we don't have enough ships with this planet, all of the others are smaller, so we definitely don't with those
                break

def attack_strongest_enemy_planet(state):
    #print("this does nothing")
    enemy_planets = [planet for planet in state.enemy_planets() 
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships) #they are sorted for number of ships
    enemy_planets.reverse()
    #my planets only contains allied planets that do not have enemy ships heading towards them 
    my_planets = [planet for planet in state.my_planets()
                  if not any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]
    my_planets.sort(key=lambda p: p.num_ships)
    #sorted by num ships and reverse so highest first
    my_planets.reverse()

    for planet in enemy_planets:
        for me in my_planets:
            required_ships = planet.num_ships + \
                                 state.distance(me.ID, planet.ID) * planet.growth_rate + 1
            if me.num_ships > required_ships:
                return issue_order(state, me.ID, planet.ID, required_ships)
            else:
                #if we don't have enough ships with this planet, all of the others are smaller, so we definitely don't with those
                break