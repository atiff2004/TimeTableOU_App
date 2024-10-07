import random
from .models import Department, Semester, Class, CourseAssignment, Schedule, Room, Timeslot, Day

def csp_initial_schedule():
    schedule = []
    course_assignments = CourseAssignment.objects.all()
    available_days = Day.objects.all()
    available_rooms = Room.objects.all()
    available_timeslots = Timeslot.objects.all()

    for course_assignment in course_assignments:
        lecture_slots, lab_slots = get_timeslot_requirements(course_assignment.course)

        # Assign lab slots (consecutive time slots)
        if lab_slots:
            for _ in range(lab_slots[0] // 2):  # Lab slots come in pairs
                day, room, timeslot = assign_lab_slot(available_days, available_rooms, available_timeslots, course_assignment)
                if day and room and timeslot:
                    next_timeslot = get_next_timeslot(timeslot)
                    if next_timeslot:
                        schedule.append((day, room, timeslot, course_assignment))
                        schedule.append((day, room, next_timeslot, course_assignment))

        # Assign lecture slots (non-consecutive time slots)
        if lecture_slots:
            for _ in range(sum(lecture_slots)):
                day, room, timeslot = assign_lecture_slot(available_days, available_rooms, available_timeslots, course_assignment)
                if day and room and timeslot:
                    schedule.append((day, room, timeslot, course_assignment))

    return schedule

def get_timeslot_requirements(course):
    lecture_hours = int(course.credit_hours)
    lab_hours = int(course.lab_crh) if course.lab_crh else 0  # Default to 0 if lab_crh is null

    lecture_slots = [1] * lecture_hours
    lab_slots = [2] if lab_hours > 0 else []  # Lab slots are consecutive (pairs)

    return lecture_slots, lab_slots

def assign_lab_slot(available_days, available_rooms, available_timeslots, course_assignment):
    max_attempts = 150
    for _ in range(max_attempts):
        day = random.choice(available_days)
        room = random.choice(available_rooms)
        timeslot = random.choice(available_timeslots)

        next_timeslot = get_next_timeslot(timeslot)

        if is_valid_consecutive_lab_assignment(day, room, timeslot, next_timeslot, course_assignment):
            return day, room, timeslot
    return None, None, None

def assign_lecture_slot(available_days, available_rooms, available_timeslots, course_assignment):
    max_attempts = 150
    for _ in range(max_attempts):
        day = random.choice(available_days)
        room = random.choice(available_rooms)
        timeslot = random.choice(available_timeslots)

        if is_valid_non_consecutive_lecture_assignment(day, room, timeslot, course_assignment):
            return day, room, timeslot
    return None, None, None

def is_valid_consecutive_lab_assignment(day, room, timeslot, next_timeslot, course_assignment):
    if not next_timeslot:
        return False

    # Check if both timeslots are free
    if Schedule.objects.filter(day=day, room=room, timeslot=timeslot).exists():
        return False
    if Schedule.objects.filter(day=day, room=room, timeslot=next_timeslot).exists():
        return False

    # Check teacher availability
    if Schedule.objects.filter(day=day, timeslot=timeslot, course_assignment__teacher=course_assignment.teacher).exists():
        return False
    if Schedule.objects.filter(day=day, timeslot=next_timeslot, course_assignment__teacher=course_assignment.teacher).exists():
        return False

    return True

def is_valid_non_consecutive_lecture_assignment(day, room, timeslot, course_assignment):
    # Ensure no room or teacher conflicts
    if Schedule.objects.filter(day=day, room=room, timeslot=timeslot).exists():
        return False
    if Schedule.objects.filter(day=day, timeslot=timeslot, course_assignment__teacher=course_assignment.teacher).exists():
        return False

    return True

def get_next_timeslot(current_timeslot):
    current_slot = current_timeslot.slot
    current_shift = current_timeslot.shift
    return Timeslot.objects.filter(shift=current_shift).filter(slot__gt=current_slot).order_by('slot').first()
import math

def evaluate_constraints(assignment):
    penalty = 0
    day, room, timeslot, course_assignment = assignment

    # Room conflict
    if Schedule.objects.filter(day=day, room=room, timeslot=timeslot).exists():
        penalty += 10

    # Teacher conflict
    if Schedule.objects.filter(day=day, timeslot=timeslot, course_assignment__teacher=course_assignment.teacher).exists():
        penalty += 200

    # Class conflict
    if Schedule.objects.filter(day=day, timeslot=timeslot, course_assignment__class_assigned=course_assignment.class_assigned).exists():
        penalty += 1500

    # Shift conflict
    if course_assignment.class_assigned.shift != timeslot.shift:
        penalty += 50

    return penalty

def simulated_annealing(schedule, initial_temp=100, cooling_rate=0.003):
    current_schedule = schedule
    current_temp = initial_temp
    best_schedule = current_schedule

    while current_temp > 1:
        new_schedule = perturb_schedule(current_schedule)
        current_cost = calculate_cost(current_schedule)
        new_cost = calculate_cost(new_schedule)

        if acceptance_probability(current_cost, new_cost, current_temp) > random.random():
            current_schedule = new_schedule

        if new_cost < calculate_cost(best_schedule):
            best_schedule = new_schedule

        current_temp *= (1 - cooling_rate)

    return best_schedule

def calculate_cost(schedule):
    return sum(evaluate_constraints(assignment) for assignment in schedule)

def perturb_schedule(schedule):
    new_schedule = schedule[:]
    idx1, idx2 = random.sample(range(len(new_schedule)), 2)
    new_schedule[idx1], new_schedule[idx2] = new_schedule[idx2], new_schedule[idx1]
    return new_schedule

def acceptance_probability(old_cost, new_cost, temperature):
    if new_cost < old_cost:
        return 1.0
    return math.exp((old_cost - new_cost) / temperature)
def fitness(schedule):
    penalty = sum(evaluate_constraints(assignment) for assignment in schedule)
    return 100 - penalty  # Fitness is higher if penalty is lower

def genetic_algorithm_optimization(schedule, population_size=100, generations=50):
    population = initialize_population(schedule, population_size)
    best_schedule = None

    for generation in range(generations):
        population = sorted(population, key=lambda s: fitness(s), reverse=True)

        if fitness(population[0]) == 100:  # A valid solution is found
            best_schedule = population[0]
            break

        population = evolve_population(population)

    return best_schedule if best_schedule else population[0]

def initialize_population(schedule, population_size):
    population = [schedule]
    for _ in range(population_size - 1):
        new_schedule = perturb_schedule(schedule)
        population.append(new_schedule)

    return population

def evolve_population(population):
    new_population = []
    elite_size = int(len(population) * 0.1)
    new_population.extend(population[:elite_size])

    while len(new_population) < len(population):
        parent1, parent2 = random.sample(population[:len(population)//2], 2)
        child1, child2 = crossover(parent1, parent2)
        child1 = mutate(child1)
        child2 = mutate(child2)

        new_population.extend([child1, child2])

    return new_population[:len(population)]

def crossover(schedule1, schedule2):
    split = len(schedule1) // 2
    return schedule1[:split] + schedule2[split:], schedule2[:split] + schedule1[split:]

def mutate(schedule):
    idx = random.randint(0, len(schedule) - 1)
    new_schedule = perturb_schedule(schedule)
    return new_schedule
def save_schedule(schedule):
    for day, room, timeslot, course_assignment in schedule:
        try:
            if not Schedule.objects.filter(day=day, room=room, timeslot=timeslot, course_assignment=course_assignment).exists():
                Schedule.objects.create(
                    day=day, room=room, timeslot=timeslot, course_assignment=course_assignment
                )
        except IntegrityError as e:
            print(f"Error saving schedule: {e}")
def generate_schedule():
    initial_schedule = csp_initial_schedule()
    improved_schedule = simulated_annealing(initial_schedule)
    optimized_schedule = genetic_algorithm_optimization(improved_schedule)
    save_schedule(optimized_schedule)
