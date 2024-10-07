import random
from .models import Department, Semester, Class, CourseAssignment, Schedule, Room, Timeslot, Day

# Constants for GA
POPULATION_SIZE = 500
NUM_GENERATIONS = 100
MUTATION_RATE = 0.1

def genetic_algorithm_schedule(population_size=POPULATION_SIZE, generations=NUM_GENERATIONS):
    population = initialize_population(population_size)
    best_schedule = None

    for generation in range(generations):
        population = sorted(population, key=lambda schedule: fitness(schedule), reverse=True)

        # Check for a valid solution in the population
        for schedule in population:
            if is_valid_schedule(schedule) and count_slots(schedule) == 28:
                print(f"Valid full schedule found at generation {generation}! Schedule: {schedule}")
                best_schedule = schedule
                break

        if best_schedule:
            break

        # If no valid schedule, generate the next population
        population = evolve_population(population)

        print(f"Generation {generation + 1} completed.")

    return best_schedule

def fitness(schedule):
    score = 0
    penalty = 0
    
    for assignment in schedule:
        day, room, timeslot, course_assignment = assignment
        penalty += evaluate_constraints(assignment)

    score = 100 - penalty
    return score

def is_valid_schedule(schedule):
    for assignment in schedule:
        if evaluate_constraints(assignment) != 0:
            return False
    return True

def count_slots(schedule):
    return len(schedule)

def evaluate_constraints(assignment):
    penalty = 0
    day, room, timeslot, course_assignment = assignment

    # Check for room conflicts
    existing_assignments = Schedule.objects.filter(day=day, room=room, timeslot=timeslot)
    if existing_assignments.exists():
        penalty += 10  # Penalty for room conflict

    # Check for teacher conflicts
    teacher_assignments = Schedule.objects.filter(day=day, timeslot=timeslot, course_assignment__teacher=course_assignment.teacher)
    if teacher_assignments.exists():
        penalty += 200  # Penalty for teacher conflict

    # Check for class conflicts (same class assigned in multiple rooms at the same time)
    class_conflicts = Schedule.objects.filter(day=day, timeslot=timeslot, course_assignment__class_assigned=course_assignment.class_assigned)
    if class_conflicts.exists():
        penalty += 1500  # High penalty for class conflict (same class assigned in multiple rooms)

    # Ensure the timeslot matches the class shift
    if course_assignment.class_assigned.shift != timeslot.shift:
        penalty += 20  # High penalty for shift conflict

    return penalty

def initialize_population(population_size):
    population = []
    available_days = Day.objects.all()
    available_rooms = Room.objects.all()
    available_timeslots = Timeslot.objects.all()
    course_assignments = CourseAssignment.objects.all()

    for _ in range(population_size):
        schedule = []
        assigned_lecture_count = {assignment.id: 0 for assignment in course_assignments}
        assigned_lab_count = {assignment.id: 0 for assignment in course_assignments}

        for course_assignment in course_assignments:
            lecture_slots, lab_slots = get_timeslot_requirements(course_assignment.course)

            # Assign lab slots
            if lab_slots:
                for _ in range(lab_slots[0] // 2):  # Assuming lab hours are in pairs
                    day, room, timeslot = assign_lab_slot(available_days, available_rooms, available_timeslots, course_assignment)
                    if day and room and timeslot:
                        next_timeslot = get_next_timeslot(timeslot)
                        if next_timeslot:
                            schedule.append((day, room, timeslot, course_assignment))
                            schedule.append((day, room, next_timeslot, course_assignment))
                            assigned_lab_count[course_assignment.id] += 2

            # Assign lecture slots
            if lecture_slots:
                for _ in range(sum(lecture_slots)):
                    day, room, timeslot = assign_lecture_slot(available_days, available_rooms, available_timeslots, course_assignment)
                    if day and room and timeslot:
                        schedule.append((day, room, timeslot, course_assignment))
                        assigned_lecture_count[course_assignment.id] += 1

        population.append(schedule)

    return population

def is_class_conflict(day, timeslot, course_assignment):
    class_conflict = Schedule.objects.filter(day=day, timeslot=timeslot, course_assignment__class_assigned=course_assignment.class_assigned)
    return class_conflict.exists()  # Return True if there's a conflict

def assign_lab_slot(available_days, available_rooms, available_timeslots, course_assignment):
    attempts = 0
    max_attempts = 150  # Increase max attempts to retry more before giving up
    
    while attempts < max_attempts:
        day = random.choice(available_days)
        room = random.choice(available_rooms)
        timeslot = random.choice(available_timeslots)

        # Ensure the shift is respected and no class conflict exists
        if is_valid_shift_assignment(day, room, timeslot, course_assignment) and not is_class_conflict(day, timeslot, course_assignment):
            if is_valid_consecutive_lab_assignment(day, room, timeslot, course_assignment):
                return day, room, timeslot  # Return valid slot

        attempts += 1

    return None, None, None

def assign_lecture_slot(available_days, available_rooms, available_timeslots, course_assignment):
    attempts = 0
    max_attempts = 150  # Increase max attempts to retry more before giving up
    
    while attempts < max_attempts:
        day = random.choice(available_days)
        room = random.choice(available_rooms)
        timeslot = random.choice(available_timeslots)

        # Ensure the shift is respected and no class conflict exists
        if is_valid_shift_assignment(day, room, timeslot, course_assignment) and not is_class_conflict(day, timeslot, course_assignment):
            if is_valid_non_consecutive_lecture_assignment(day, room, timeslot, course_assignment):
                return day, room, timeslot  # Return valid slot
        attempts += 1

    return None, None, None

def get_timeslot_requirements(course):
    try:
        lecture_hours = int(course.credit_hours)
        lab_hours = course.lab_crh
    except ValueError:
        raise ValueError(f"Invalid credit hour format for course: {course.short_name}. Ensure credit hours are integers.")

    lecture_slots = []
    lab_slots = []

    if lecture_hours == 3:
        lecture_slots.extend([1, 1])  # 3 credit hours can be divided into 2 slots
    elif lecture_hours == 2:
        lecture_slots.append(1)
    elif lecture_hours == 1:
        lecture_slots.append(1)

    if lab_hours > 0:
        lab_slots.append(2)  # Lab hours are typically assigned in pairs

    return lecture_slots, lab_slots

def is_valid_non_consecutive_lecture_assignment(day, room, timeslot, course_assignment):
    existing_assignments = Schedule.objects.filter(day=day, room=room, timeslot=timeslot)
    if existing_assignments.exists():
        return False

    next_timeslot = get_next_timeslot(timeslot)
    if next_timeslot:
        existing_assignments_next = Schedule.objects.filter(day=day, room=room, timeslot=next_timeslot, course_assignment__class_assigned=course_assignment.class_assigned)
        if existing_assignments_next.exists():
            return False

    return True

def is_valid_consecutive_lab_assignment(day, room, timeslot, course_assignment):
    next_timeslot = get_next_timeslot(timeslot)
    if not next_timeslot:
        return False

    current_slot_occupied = Schedule.objects.filter(day=day, room=room, timeslot=timeslot).exists()
    next_slot_occupied = Schedule.objects.filter(day=day, room=room, timeslot=next_timeslot).exists()

    if current_slot_occupied or next_slot_occupied:
        return False

    if course_assignment.course.lab_crh > 0:
        return True

    return False

def is_valid_shift_assignment(day, room, timeslot, course_assignment):
    class_shift = course_assignment.class_assigned.shift.name
    timeslot_shift = timeslot.shift.name
    return class_shift == timeslot_shift

def evolve_population(population):
    new_population = []
    elite_size = int(len(population) * 0.1)
    new_population.extend(population[:elite_size])

    while len(new_population) < len(population):
        parent1, parent2 = random.choices(population[:len(population)//2], k=2)
        child1, child2 = crossover(parent1, parent2)

        child1 = mutate(child1) if random.random() < MUTATION_RATE else child1
        child2 = mutate(child2) if random.random() < MUTATION_RATE else child2

        new_population.extend([child1, child2])

    return new_population[:len(population)]

def crossover(schedule1, schedule2):
    split_index = len(schedule1) // 2
    child1 = schedule1[:split_index] + schedule2[split_index:]
    child2 = schedule2[:split_index] + schedule1[split_index:]
    return child1, child2

def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    day = random.choice(Day.objects.all())
    room = random.choice(Room.objects.all())
    timeslot = random.choice(Timeslot.objects.all())
    course_assignment = schedule[mutation_point][3]

    if course_assignment.course.lab_crh > 0:
        if is_valid_consecutive_lab_assignment(day, room, timeslot, course_assignment):
            next_timeslot = get_next_timeslot(timeslot)
            if next_timeslot:
                schedule[mutation_point] = (day, room, timeslot, course_assignment)
                schedule[mutation_point + 1] = (day, room, next_timeslot, course_assignment)
    else:
        if is_valid_non_consecutive_lecture_assignment(day, room, timeslot, course_assignment):
            schedule[mutation_point] = (day, room, timeslot, course_assignment)

    return schedule

def get_next_timeslot(current_timeslot):
    current_slot = current_timeslot.slot
    current_shift = current_timeslot.shift
    next_timeslot = (
        Timeslot.objects.filter(shift=current_shift)
        .filter(slot__gt=current_slot)
        .order_by('slot')
        .first()
    )
    return next_timeslot

