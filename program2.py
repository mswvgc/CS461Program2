# Michael Wright
# mswvgc@umsystem.edu
# 04/15/2022
# CS461 Program 2

import random
import numpy as np
import json
from scipy.special import softmax

# Define the rooms dictionary with 'capacity' and 'building' keys
rooms = {
    "Slater 003": {"capacity": 45, "building": "Slater"},
    "Roman 216": {"capacity": 30, "building": "Roman"},
    "Loft 206": {"capacity": 75, "building": "Loft"},
    "Roman 201": {"capacity": 50, "building": "Roman"},
    "Loft 310": {"capacity": 108, "building": "Loft"},
    "Beach 201": {"capacity": 60, "building": "Beach"},
    "Beach 301": {"capacity": 75, "building": "Beach"},
    "Logos 325": {"capacity": 450, "building": "Logos"},
    "Frank 119": {"capacity": 60, "building": "Frank"}
}

# Define the available time slots within a set
times = [10,11,12,1,2,3]

# Define the activities dictionary with 'enrollment', 'preferred_facilitators', and 'other_facilitators' keys
activities = {
    "SLA101A": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA101B": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA191A": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA191B": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA201": {"enrollment": 50, "preferred_facilitators": ["Glen", "Banks", "Zeldin", "Shaw"], "other_facilitators": ["Numen", "Richards", "Singer"]},
    "SLA291": {"enrollment": 50, "preferred_facilitators": ["Lock", "Banks", "Zeldin", "Singer"], "other_facilitators": ["Numen", "Richards", "Shaw", "Tyler"]},
    "SLA303": {"enrollment": 60, "preferred_facilitators": ["Glen", "Zeldin", "Banks"], "other_facilitators": ["Numen", "Singer", "Shaw"]},
    "SLA304": {"enrollment": 25, "preferred_facilitators": ["Glen", "Banks", "Tyler"], "other_facilitators": ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]},
    "SLA394": {"enrollment": 20, "preferred_facilitators": ["Tyler", "Singer"], "other_facilitators": ["Richards", "Zeldin"]},
    "SLA449": {"enrollment": 60, "preferred_facilitators": ["Tyler", "Singer", "Shaw"], "other_facilitators": ["Zeldin", "Uther"]},
    "SLA451": {"enrollment": 100, "preferred_facilitators": ["Tyler", "Singer", "Shaw"], "other_facilitators": ["Zeldin", "Uther", "Richards", "Banks"]},
}

# Define the entire set of facilitators for selecting faculty
all_facilitators = {"Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"}

# Generates the initial list of random schedules
def generate_initial_population(population_size=500):
    population = []

    for _ in range(population_size):
        schedule = {}

        # Assign random rooms, facilitators, and time slots for each activity
        for activity in activities:
            room = random.choice(list(rooms.keys()))
            time = random.choice(times)
            facilitator = random.choice(list(all_facilitators))

            # Store the activity, room, facilitator, and time in a dictionary
            schedule[activity] = {
                "room": room,
                "time": time,
                "facilitator": facilitator
            }
            
        # Append the generated schedule to the population list
        population.append(schedule)

    # Return the list of generated schedules
    return population

# Calculates the fitness score of a given schedule
def calculate_fitness(schedule):
    fitness = 0

    # Initialize dictionaries to keep track of facilitator time slots,
    # the last time a facilitator was scheduled, and the last room a facilitator was scheduled
    facilitator_time_slots = {}
    facilitator_last_time = {}
    facilitator_last_room = {}

    # Initialize lists to store the time slots and rooms of SLA 101 and SLA 191 sections
    sla_101_sections = []
    sla_191_sections = []

    # Loop through each activity in the schedule
    for activity in schedule:
        # Initialize the fitness score for the current activity to 0
        activity_fitness = 0
        room = schedule[activity]['room']
        facilitator = schedule[activity]['facilitator']
        time_slot = schedule[activity]['time']

        # Activity is scheduled at the same time in the same room as another of the activities: -0.5
        for other_activity in schedule:
            if activity != other_activity:
                if schedule[other_activity]['room'] == room and schedule[other_activity]['time'] == time_slot:
                    activity_fitness -= 0.5

        # Room size
        # Activity is in a room too small for its expected enrollment: -0.5
        if rooms[room]['capacity'] < activities[activity]['enrollment']:
            activity_fitness -= 0.5
        # Activity is in a room with capacity > 6 times expected enrollment: -0.4
        elif rooms[room]['capacity']  > 6 * activities[activity]['enrollment']:
            activity_fitness -= 0.4
        # Activity is in a room with capacity > 3 times expected enrollment: -0.2
        elif rooms[room]['capacity']  > 3 * activities[activity]['enrollment']:
            activity_fitness -= 0.2
        else:  # Otherwise + 0.3
            activity_fitness += 0.3

        # Facilitators
        # Activities is overseen by a preferred facilitator: + 0.5
        if facilitator == activities[activity]['preferred_facilitators']:
            activity_fitness += 0.5
        # Activities is overseen by another facilitator listed for that activity: +0.2
        elif facilitator in activities[activity]['other_facilitators']:
            activity_fitness += 0.2
        else:  # Activities is overseen by some other facilitator: -0.1
            activity_fitness -= 0.1

        # Check facilitator load
        if facilitator not in facilitator_time_slots:
            facilitator_time_slots[facilitator] = []

        # Add the time slot to the facilitator's list of scheduled time slots
        facilitator_time_slots[facilitator].append(time_slot)

        # Activity facilitator is scheduled for more than one activity at the same time: - 0.2
        if facilitator_time_slots[facilitator].count(time_slot) > 1:
            activity_fitness -= 0.2

        total_activities = len(facilitator_time_slots[facilitator])
        # Facilitator is scheduled to oversee more than 4 activities total: -0.5
        if total_activities > 4:
            activity_fitness -= 0.5
        # Facilitator is scheduled to oversee 1 or 2 activities: -0.4
        elif total_activities == 1 or total_activities == 2:
            if facilitator != "Dr. Tyler":
                activity_fitness -= 0.4

        # No consecutive time slots for facilitators
        if facilitator in facilitator_last_time:
            if abs(time_slot - facilitator_last_time[facilitator]) == 1:
                activity_fitness += 0.5

                # Check if one activity is in Roman or Beach, and the other isn't
                if ("Roman" in room and "Beach" not in facilitator_last_room[facilitator]) or \
                        ("Beach" in room and "Roman" not in facilitator_last_room[facilitator]) or \
                        ("Roman" in facilitator_last_room[facilitator] and "Beach" not in room) or \
                        ("Beach" in facilitator_last_room[facilitator] and "Roman" not in room):
                    activity_fitness -= 0.4

        # Dictionaries are updated to store the current time_slot/room for each facilitator
        facilitator_last_time[facilitator] = time_slot
        facilitator_last_room[facilitator] = room

        if activity.startswith("SLA101"):
            sla_101_sections.append((time_slot, room))
        elif activity.startswith("SLA191"):
            sla_191_sections.append((time_slot, room))

        # Score calculated for the activity is added to the overall fitness score for the schedule.
        fitness += activity_fitness
        # Jump to start of loop
        
    # Add constraints specific to SLA101 and SLA191 courses
    # The 2 sections of SLA 101 are more than 4 hours apart: + 0.5
    if abs(sla_101_sections[0][0] - sla_101_sections[1][0]) > 4:
        fitness += 0.5

    # Both sections of SLA 101 are in the same time slot: -0.5
    if sla_101_sections[0][0] == sla_101_sections[1][0]:
        fitness -= 0.5

    # The 2 sections of SLA 191 are more than 4 hours apart: + 0.5
    if abs(sla_191_sections[0][0] - sla_191_sections[1][0]) > 4:
        fitness += 0.5

    # Both sections of SLA 191 are in the same time slot: -0.5
    if sla_191_sections[0][0] == sla_191_sections[1][0]:
        fitness -= 0.5

    # A section of SLA 191 and a section of SLA 101 are overseen in consecutive time slots: +0.5
    for sla_101_slot, sla_101_room in sla_101_sections:
        for sla_191_slot, sla_191_room in sla_191_sections:
            if abs(sla_101_slot - sla_191_slot) == 1:
                fitness += 0.5

                # One of the activities is in Roman or Beach, and the other isn't: -0.4
                if (sla_101_room in ["Roman", "Beach"]) != (sla_191_room in ["Roman", "Beach"]):
                    fitness -= 0.4

    # A section of SLA 191 and a section of SLA 101 are taught separated by 1 hour: + 0.25
    for sla_101_slot, _ in sla_101_sections:
        for sla_191_slot, _ in sla_191_sections:
            if abs(sla_101_slot - sla_191_slot) == 2:
                fitness += 0.25

    # A section of SLA 191 and a section of SLA 101 are taught in the same time slot: -0.25
    for sla_101_slot, _ in sla_101_sections:
        for sla_191_slot, _ in sla_191_sections:
            if sla_101_slot == sla_191_slot:
                fitness -= 0.25

    return fitness


def genetic_algorithm(population, mutation_rate=0.01):
    generation = 0
    fitness_scores_history = []

    while generation < 100:
        # Calculate fitness scores for the current population
        fitness_scores = [calculate_fitness(schedule) for schedule in population]

        # Selection
        selected_parent1, selected_parent2 = selection(population, fitness_scores)

        # Reproduction
        offspring_schedules = crossover(selected_parent1, selected_parent2)

        # Mutation
        mutated_schedules = mutate(offspring_schedules, mutation_rate)

        # Replacement
        population = replacement(population, mutated_schedules)

        # Add the current average fitness score to the history
        fitness_scores_history.append(np.mean(fitness_scores))

        # Check for convergence
        if len(fitness_scores_history) > 100:
            improvement = (fitness_scores_history[-1] - fitness_scores_history[-101]) / fitness_scores_history[-101]
            if improvement < 0.01:
                break

        generation += 1

    # Return the best schedule found
    best_schedule_index = np.argmax(fitness_scores)
    return population[best_schedule_index]

# The mutation rate is dynamically adjusted based on the history of fitness scores
def adaptive_genetic_algorithm(population, initial_mutation_rate=0.01):
    mutation_rate = initial_mutation_rate
    previous_best_fitness = -np.inf
    best_schedule = None

    while True:
        current_best_schedule = genetic_algorithm(population, mutation_rate)
        current_best_fitness = calculate_fitness(current_best_schedule)

        # If the fitness is not improving by atleast 1%, break the loop
        if current_best_fitness <= previous_best_fitness * (1 + 0.01):
            break

        # Update the best schedule and fitness
        best_schedule = current_best_schedule
        previous_best_fitness = current_best_fitness

        # Reduce the mutation rate by half
        mutation_rate /= 2

    return best_schedule


def selection(population, fitness_scores):

    # Normalize fitness scores using softmax normalization
    probabilities = softmax(fitness_scores)

    # Use weighted random selection to choose individuals for reproduction
    selected_indices = np.random.choice(len(population), size=len(population) // 2, p=probabilities)

    # Return the two selected parents
    return population[selected_indices[0]], population[selected_indices[1]]

def crossover(parent1, parent2):
    # Convert the parent dictionaries to lists of key-value tuples
    parent1_list = list(parent1.items())
    parent2_list = list(parent2.items())

    # Randomly choose a crossover point
    crossover_point = random.randint(1, len(parent1_list) - 1)

    # Combine the left part of parent1_list and right part of parent2_list
    child1_list = parent1_list[:crossover_point] + parent2_list[crossover_point:]

    # Combine the left part of parent2_list and right part of parent1_list
    child2_list = parent2_list[:crossover_point] + parent1_list[crossover_point:]

    # Convert the child lists back to dictionaries
    child1 = dict(child1_list)
    child2 = dict(child2_list)

    # Return the offspring as a tuple
    return child1, child2


def mutate(offspring_schedules, mutation_rate):
    mutated_schedules = []

    # Iterate through each schedule in offspring_schedules
    for schedule in offspring_schedules:
        # If the random number generated is less than the mutation rate,
        # mutate the schedule and append it to the mutated_schedules list.
        # Otherwise, append the original schedule to the mutated_schedules list
        if random.random() < mutation_rate:
            # Choose a random activity in the schedule to mutate
            activity_key = random.choice(list(schedule.keys()))
            # Get the original activity details from the schedule
            original_activity = schedule[activity_key]
            # Choose a random new activity to replace the original activity
            mutated_activity = random.choice(list(activities.values()))
            # Replace the original activity in the schedule with the mutated activity
            schedule[activity_key] = mutated_activity

            # If the mutated activity doesn't have a room/facilitator/time specified, use the original values
            if 'room' not in mutated_activity:
                mutated_activity['room'] = original_activity['room']
            if 'facilitator' not in mutated_activity:
                mutated_activity['facilitator'] = original_activity['facilitator']
            if 'time' not in mutated_activity:
                mutated_activity['time'] = original_activity['time']

            # Add the mutated schedule to the list of mutated schedules
            mutated_schedules.append(schedule)
        else:
            # If the schedule wasn't mutated, add it to the list of mutated schedules unchanged
            mutated_schedules.append(schedule)

    return mutated_schedules


def replacement(population, mutated_schedules):
    # Convert the mutated_schedules tuple to a list
    mutated_schedules_list = list(mutated_schedules)

    # Combine the population and mutated schedules
    combined_population = population + mutated_schedules_list

    # Sort the combined population by their fitness scores in descending order
    combined_population.sort(key=lambda x: calculate_fitness(x), reverse=True)

    # Keep the top 50% of the combined population
    new_population = combined_population[:len(population)]

    return new_population


def main():
    # Parameters
    population_size = 500
    initial_mutation_rate = 0.01

    # Generate initial population of schedules
    population = generate_initial_population(population_size)

    # Call the adaptive_genetic_algorithm function to find the best schedule in the population
    best_schedule = adaptive_genetic_algorithm(population, initial_mutation_rate)

    # Use the best schedule
    print("Best schedule found:")
    print(json.dumps(best_schedule, indent=4))  # Format as JSON and print

    # Write the best schedule to a JSON file
    with open("best_schedule.json", "w") as output_file:
        json.dump(best_schedule, output_file, indent=4)

if __name__ == "__main__":
    main()
