import random
from collections import defaultdict

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

times = [10,11,12,1,2,3]

activities = {
    "SLA100A": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
    "SLA100B": {"enrollment": 50, "preferred_facilitators": ["Glen", "Lock", "Banks", "Zeldin"], "other_facilitators": ["Numen", "Richards"]},
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

all_facilitators = {"Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"}

def generate_initial_population(population_size=500):
    population = []

    for _ in range(population_size):
        schedule = {}

        for activity in activities:
            room = random.choice(list(rooms.keys()))
            time = random.choice(times)
            facilitator = random.choice(list(all_facilitators))

            schedule[activity] = {
                "room": room,
                "time": time,
                "facilitator": facilitator
            }

        population.append(schedule)

    return population


def calculate_fitness(schedule):
    fitness = 0
    facilitator_load = {}
    facilitator_time_slots = {}

    for facilitator in all_facilitators:
        facilitator_load[facilitator] = 0
        facilitator_time_slots[facilitator] = {}

    for activity, data in schedule.items():
        room_capacity = int(rooms[data["room"]]["capacity"])
        expected_enrollment = int(activities[activity]["enrollment"])
        facilitator = data["facilitator"]
        time_slot = data["time"]

        facilitator_load[facilitator] += 1
        if time_slot not in facilitator_time_slots[facilitator]:
            facilitator_time_slots[facilitator][time_slot] = 0
        facilitator_time_slots[facilitator][time_slot] += 1

        if room_capacity < expected_enrollment:
            fitness -= 0.5
        elif room_capacity > 3 * expected_enrollment:
            fitness -= 0.2
        elif room_capacity > 6 * expected_enrollment:
            fitness -= 0.4
        else:
            fitness += 0.3

        if facilitator in activities[activity]["preferred_facilitators"]:
            fitness += 0.5
        elif facilitator in activities[activity]["other_facilitators"]:
            fitness += 0.2
        else:
            fitness -= 0.1

        facilitator_time_slots = defaultdict(set)
        for activity in schedule:
            facilitator_time_slots[schedule[activity]["facilitator"]].add(schedule[activity]["time"])

            for facilitator, time_slots in facilitator_time_slots.items():
                sorted_time_slots = sorted([times.index(slot) for slot in time_slots])
                for i in range(1, len(sorted_time_slots)):
                    time_diff = sorted_time_slots[i] - sorted_time_slots[i - 1]
                    if time_diff == 1:
                        fitness += 0.5
                        if (rooms[schedule[activity]["room"]]["building"] in ["Roman", "Beach"]) != (
                                rooms[schedule[activity]["room"]]["building"] in ["Roman", "Beach"]):
                            fitness -= 0.4

        for facilitator, load in facilitator_load.items():
            time_slots = facilitator_time_slots[facilitator]

            for slot in time_slots:
                count = time_slots[slot]
                if count == 1:
                    fitness += 0.2
                elif count > 1:
                    fitness -= 0.2

            if load > 4:
                fitness -= 0.5
            elif load == 1 or load == 2 and facilitator != "Dr. Tyler":
                fitness -= 0.4



            sorted_time_slots = sorted(list(time_slots.keys()))
            for i in range(1, len(sorted_time_slots)):
                if sorted_time_slots[i] - sorted_time_slots[i - 1] == 1:
                    fitness -= 0.5

        sla_101_sections = [activity for activity in schedule if activity.startswith("SLA101")]
        sla_191_sections = [activity for activity in schedule if activity.startswith("SLA191")]

        for sla_101_section in sla_101_sections:
            for sla_191_section in sla_191_sections:
                time_diff = abs(schedule[sla_101_section]["time"] - schedule[sla_191_section]["time"])
                if time_diff == 1:
                    fitness += 0.5
                    if (rooms[schedule[sla_101_section]["room"]]["building"] in ["Roman", "Beach"]) != (
                            rooms[schedule[sla_191_section]["room"]]["building"] in ["Roman", "Beach"]):
                        fitness -= 0.4
                elif time_diff == 2:
                    fitness += 0.25
                elif time_diff == 0:
                    fitness -= 0.25

        return fitness

def main():
    population = generate_initial_population()

    for i in range(5):
        print(f"Schedule {i + 1}: {population[i]}")

    fitness_scores = []
    for schedule in population:
        fitness = calculate_fitness(schedule)
        fitness_scores.append(fitness)

    for i in range(5):
        print(f"Schedule {i + 1} fitness: {fitness_scores[i]}")

   

if __name__ == "__main__":
    main()
