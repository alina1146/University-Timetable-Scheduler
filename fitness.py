# =============================================================================
# fitness.py — How Good Is This Timetable?
# =============================================================================
# This file does ONE job: look at a chromosome (timetable) and give it a score.
#
# The score tells the GA:
#   "This timetable is great, keep it"  → high fitness (close to 1.0)
#   "This timetable is terrible, drop it" → low fitness (close to 0.0)
#
# HOW SCORING WORKS:
#   1. Go through every pair of genes (every pair of courses)
#   2. Check if they clash — using your hard and soft constraints
#   3. Add a penalty for each violation found
#   4. Convert total penalty → a fitness score between 0 and 1
#
# PENALTY SYSTEM (directly from your proposal document):
#   Hard constraint violation → +10 penalty  (must fix these)
#   Soft constraint violation →  +2 penalty  (nice to fix)
#
# FITNESS FORMULA:
#   fitness = 1 / (1 + total_penalty)
#
#   → penalty = 0  : fitness = 1/(1+0)  = 1.0  ✅ perfect timetable
#   → penalty = 10 : fitness = 1/(1+10) = 0.09 ❌ one hard clash
#   → penalty = 2  : fitness = 1/(1+2)  = 0.33 ⚠ one soft violation
#
# The GA always tries to MAXIMIZE fitness (push it toward 1.0).
# =============================================================================

from chromosome import Chromosome


# -----------------------------------------------------------------------------
# HARD CONSTRAINT 1: Room Clash
# -----------------------------------------------------------------------------
# Two courses cannot be in the SAME room at the SAME time.
#
# How to check:
#   Compare every pair of genes.
#   If gene_A.room == gene_B.room AND gene_A.time_slot == gene_B.time_slot
#   → that's a room clash → +10 penalty
#
# Real example from our data:
#   C1 → R1, Monday 9am
#   C3 → R1, Monday 9am   ← CLASH! Same room, same slot

def check_room_clash(gene_a, gene_b):
    """Returns 10 if two genes share the same room and time slot, else 0."""
    if (gene_a.room.room_id == gene_b.room.room_id and
            gene_a.time_slot.slot_id == gene_b.time_slot.slot_id):
        return 10
    return 0


# -----------------------------------------------------------------------------
# HARD CONSTRAINT 2: Instructor Clash
# -----------------------------------------------------------------------------
# An instructor cannot teach TWO courses at the SAME time.
#
# How to check:
#   If gene_A.course.instructor == gene_B.course.instructor
#   AND gene_A.time_slot == gene_B.time_slot
#   → instructor clash → +10 penalty
#
# Real example from our data:
#   C1 taught by T1 (Umber Nisar) → Monday 9am
#   C4 taught by T1 (Umber Nisar) → Monday 9am  ← CLASH! Same teacher

def check_instructor_clash(gene_a, gene_b):
    """Returns 10 if two genes have the same instructor at the same time, else 0."""
    if (gene_a.course.instructor.instructor_id ==
            gene_b.course.instructor.instructor_id and
            gene_a.time_slot.slot_id == gene_b.time_slot.slot_id):
        return 10
    return 0


# -----------------------------------------------------------------------------
# HARD CONSTRAINT 3: Student Clash
# -----------------------------------------------------------------------------
# Students enrolled in multiple courses cannot have overlapping schedules.
#
# How to check:
#   Find students enrolled in BOTH course_A and course_B (set intersection).
#   If there's any overlap AND they're scheduled at the same time → clash → +10
#
# Real example from our data:
#   C1 has students S1–S30
#   C2 has students S10–S40
#   S10–S30 are in BOTH → if C1 and C2 are at the same time, those 21 students clash

def check_student_clash(gene_a, gene_b):
    """Returns 10 if shared students have overlapping schedules, else 0."""
    if gene_a.time_slot.slot_id == gene_b.time_slot.slot_id:
        shared_students = set(gene_a.course.students) & set(gene_b.course.students)
        if shared_students:
            return 10
    return 0


# -----------------------------------------------------------------------------
# SOFT CONSTRAINT: Room Capacity
# -----------------------------------------------------------------------------
# The room should be big enough for all enrolled students.
# This is "soft" because a slightly small room isn't a disaster — just not ideal.
#
# How to check:
#   If room.capacity < number of students in course → +2 penalty
#
# Real example from our data:
#   C4 has 31 students → assigned R3 (capacity 30) → doesn't fit! → +2

def check_room_capacity(gene):
    """Returns 2 if the room is too small for the course's students, else 0."""
    if gene.room.capacity < len(gene.course.students):
        return 2
    return 0


# -----------------------------------------------------------------------------
# MAIN FITNESS FUNCTION
# -----------------------------------------------------------------------------
# This is the function called on every chromosome in the population.
#
# It does two passes:
#
#   PASS 1 — Pairwise checks (compare every course against every other course)
#     For each unique pair (C1,C2), (C1,C3), (C1,C4), (C2,C3), (C2,C4), (C3,C4):
#       → Check room clash
#       → Check instructor clash
#       → Check student clash
#
#   PASS 2 — Individual checks (look at each course on its own)
#       → Check room capacity
#
# Then compute: fitness = 1 / (1 + total_penalty)
# Store the score inside the chromosome itself (chromosome.fitness)

def calculate_fitness(chromosome: Chromosome) -> float:
    total_penalty = 0
    violations    = []   # we'll collect descriptions for the self-test printout

    genes = chromosome.genes

    # ------------------------------------------------------------------
    # PASS 1: Pairwise constraint checks
    # ------------------------------------------------------------------
    # range(len) with a nested j = i+1 ensures we check each PAIR only once.
    # Without the i+1 trick, we'd double-count every clash.
    #
    # With 4 courses, the pairs are: (0,1),(0,2),(0,3),(1,2),(1,3),(2,3) = 6 pairs

    for i in range(len(genes)):
        for j in range(i + 1, len(genes)):
            gene_a = genes[i]
            gene_b = genes[j]

            # Hard Constraint 1: Room clash
            penalty = check_room_clash(gene_a, gene_b)
            if penalty:
                total_penalty += penalty
                violations.append(
                    f"  ❌ ROOM CLASH (+10):       "
                    f"{gene_a.course.course_id} & {gene_b.course.course_id} "
                    f"both in {gene_a.room.room_id} at {gene_a.time_slot}"
                )

            # Hard Constraint 2: Instructor clash
            penalty = check_instructor_clash(gene_a, gene_b)
            if penalty:
                total_penalty += penalty
                violations.append(
                    f"  ❌ INSTRUCTOR CLASH (+10): "
                    f"{gene_a.course.course_id} & {gene_b.course.course_id} "
                    f"— {gene_a.course.instructor.name} at {gene_a.time_slot}"
                )

            # Hard Constraint 3: Student clash
            penalty = check_student_clash(gene_a, gene_b)
            if penalty:
                shared = set(gene_a.course.students) & set(gene_b.course.students)
                total_penalty += penalty
                violations.append(
                    f"  ❌ STUDENT CLASH (+10):    "
                    f"{gene_a.course.course_id} & {gene_b.course.course_id} "
                    f"share {len(shared)} students at {gene_a.time_slot}"
                )

    # ------------------------------------------------------------------
    # PASS 2: Individual gene checks
    # ------------------------------------------------------------------
    for gene in genes:

        # Soft Constraint: Room capacity
        penalty = check_room_capacity(gene)
        if penalty:
            total_penalty += penalty
            violations.append(
                f"  ⚠️  CAPACITY ISSUE (+2):    "
                f"{gene.course.course_id} has {len(gene.course.students)} students"
                f" but {gene.room.room_id} fits only {gene.room.capacity}"
            )

    # ------------------------------------------------------------------
    # Compute and store fitness
    # ------------------------------------------------------------------
    fitness = 1 / (1 + total_penalty)
    chromosome.fitness   = fitness
    chromosome.penalty   = total_penalty    # store penalty too (useful for reports)
    chromosome.violations = violations      # store descriptions (useful for debug)

    return fitness


# =============================================================================
# QUICK SELF-TEST
# =============================================================================
# Run: python fitness.py
#
# Test A: A deliberately BAD timetable (all courses in same room, same slot)
#          → should have maximum clashes, very low fitness
#
# Test B: A PERFECT timetable (all courses in different rooms and slots)
#          → should have zero clashes, fitness = 1.0
#
# Test C: A random timetable from chromosome.py
#          → somewhere in between
# =============================================================================

if __name__ == "__main__":

    from data import courses, rooms, time_slots
    from chromosome import Gene, Chromosome, create_random_chromosome
    import random

    # ------------------------------------------------------------------
    # TEST A: Worst possible timetable — every course in R1 at Monday 9am
    # ------------------------------------------------------------------
    print("=" * 60)
    print("TEST A: WORST TIMETABLE (all same room + same slot)")
    print("=" * 60)

    worst_genes = [
        Gene(courses[0], rooms[0], time_slots[0]),  # C1 → R1, TS1
        Gene(courses[1], rooms[0], time_slots[0]),  # C2 → R1, TS1
        Gene(courses[2], rooms[0], time_slots[0]),  # C3 → R1, TS1
        Gene(courses[3], rooms[0], time_slots[0]),  # C4 → R1, TS1
    ]
    worst = Chromosome(worst_genes)
    calculate_fitness(worst)

    print(f"\nViolations found:")
    for v in worst.violations:
        print(v)
    print(f"\nTotal Penalty : {worst.penalty}")
    print(f"Fitness Score : {worst.fitness:.4f}  ← very low, terrible timetable")

    # ------------------------------------------------------------------
    # TEST B: Perfect timetable — every course in different room + slot
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("TEST B: PERFECT TIMETABLE (no clashes at all)")
    print("=" * 60)

    perfect_genes = [
        Gene(courses[0], rooms[0], time_slots[0]),  # C1 → R1, TS1
        Gene(courses[1], rooms[1], time_slots[1]),  # C2 → R2, TS2
        Gene(courses[2], rooms[2], time_slots[2]),  # C3 → R3, TS3
        Gene(courses[3], rooms[0], time_slots[3]),  # C4 → R1, TS4
    ]
    perfect = Chromosome(perfect_genes)
    calculate_fitness(perfect)

    print(f"\nViolations found: none" if not perfect.violations else "")
    for v in perfect.violations:
        print(v)
    print(f"Total Penalty : {perfect.penalty}")
    print(f"Fitness Score : {perfect.fitness:.4f}  ← 1.0 means perfect!")

    # ------------------------------------------------------------------
    # TEST C: Random timetable — somewhere in between
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("TEST C: RANDOM TIMETABLE (typical GA starting point)")
    print("=" * 60)

    random.seed(99)
    random_chrom = create_random_chromosome()
    calculate_fitness(random_chrom)

    print(f"\nTimetable:")
    for gene in random_chrom.genes:
        print(f"  {gene}")
    print(f"\nViolations found:")
    if random_chrom.violations:
        for v in random_chrom.violations:
            print(v)
    else:
        print("  None! Lucky random draw.")
    print(f"\nTotal Penalty : {random_chrom.penalty}")
    print(f"Fitness Score : {random_chrom.fitness:.4f}")
