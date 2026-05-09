# =============================================================================
# chromosome.py — What a "Timetable" Looks Like to the Genetic Algorithm
# =============================================================================
# In a Genetic Algorithm, every candidate solution is called a CHROMOSOME.
# In our problem, one chromosome = one complete timetable.
#
# A timetable answers this question for every course:
#   "Which room and which time slot is this course assigned to?"
#
# So a chromosome is just a list of GENES, where:
#   one gene = one course's assignment = (Course, Room, TimeSlot)
#
# Visual example of one chromosome (one timetable):
#
#   Gene 0:  C1 (Data Structures)   → R1, Monday    9–10am
#   Gene 1:  C2 (AI Fundamentals)   → R2, Monday   10–11am
#   Gene 2:  C3 (Databases)         → R1, Tuesday   9–10am
#   Gene 3:  C4 (Operating Systems) → R3, Tuesday  10–11am
#
# This chromosome may or may not have conflicts — that's the fitness
# function's job to check (next file: fitness.py).
#
# This file's job: CREATE and STORE timetables. Nothing more.
# =============================================================================

import random
from data import courses, rooms, time_slots


# -----------------------------------------------------------------------------
# PART 1: Gene
# -----------------------------------------------------------------------------
# A Gene is the smallest unit of a chromosome.
# It represents ONE course's complete scheduling decision:
#   → which room it's in
#   → which time slot it occupies
#
# Every course gets exactly one Gene. 4 courses = 4 genes per chromosome.

class Gene:
    def __init__(self, course, room, time_slot):
        self.course    = course      # Course object  (e.g. C1 - Data Structures)
        self.room      = room        # Room object    (e.g. R1, capacity 50)
        self.time_slot = time_slot   # TimeSlot object (e.g. Monday 9–10am)

    def __repr__(self):
        return (f"{self.course.course_id} ({self.course.name})"
                f" → {self.room.room_id}, {self.time_slot}")


# -----------------------------------------------------------------------------
# PART 2: Chromosome
# -----------------------------------------------------------------------------
# A Chromosome is a complete timetable — a list of Genes, one per course.
#
# It also stores a FITNESS SCORE once it's been evaluated.
# (fitness starts as None — it gets filled in by fitness.py)

class Chromosome:
    def __init__(self, genes):
        self.genes   = genes    # list of Gene objects, one per course
        self.fitness = None     # will be set by fitness.py later

    def __repr__(self):
        lines = ["--- Timetable ---"]
        for gene in self.genes:
            lines.append(f"  {gene}")
        if self.fitness is not None:
            lines.append(f"  Fitness Score: {self.fitness:.4f}")
        return "\n".join(lines)


# -----------------------------------------------------------------------------
# PART 3: Random Chromosome Generator
# -----------------------------------------------------------------------------
# This creates ONE random timetable.
#
# How it works:
#   For each course, randomly pick any room and any time slot.
#   No checking for conflicts here — randomness means most will have clashes.
#   That's completely fine! The GA's job is to fix them over generations.
#
# Think of it like shuffling a deck of cards — you start with a random order
# and then sort it. You don't try to build the sorted order from scratch.

def create_random_chromosome():
    genes = []
    for course in courses:
        random_room      = random.choice(rooms)
        random_time_slot = random.choice(time_slots)
        genes.append(Gene(course, random_room, random_time_slot))
    return Chromosome(genes)


# -----------------------------------------------------------------------------
# PART 4: Population Generator
# -----------------------------------------------------------------------------
# A POPULATION is a collection of multiple chromosomes (timetables).
#
# Why many at once?
#   The GA doesn't work on one timetable — it works on a whole group.
#   It picks the best ones, mixes them, and makes new ones.
#   The larger the population, the more variety — but also slower to compute.
#
# For our project, a population of 10 is fine for the sample dataset.
# With real data (more courses), you'd increase this to 50–100.

def create_population(size=10):
    return [create_random_chromosome() for _ in range(size)]


# =============================================================================
# QUICK SELF-TEST
# =============================================================================
# Run: python chromosome.py
# You'll see a random population of 3 timetables.
# Every time you run it, the timetables will be different (random).
# =============================================================================

if __name__ == "__main__":

    random.seed(42)  # seed makes output consistent so you can follow along
                     # remove this line later for true randomness

    print("=" * 55)
    print("SINGLE RANDOM CHROMOSOME (one timetable)")
    print("=" * 55)
    chrom = create_random_chromosome()
    print(chrom)

    print("\n" + "=" * 55)
    print("POPULATION OF 3 RANDOM CHROMOSOMES")
    print("=" * 55)
    population = create_population(size=3)
    for i, chrom in enumerate(population):
        print(f"\nChromosome #{i + 1}:")
        for gene in chrom.genes:
            print(f"  {gene}")

    print("\n" + "=" * 55)
    print("KEY FACTS ABOUT THIS POPULATION")
    print("=" * 55)
    print(f"  Total chromosomes  : {len(population)}")
    print(f"  Genes per chrom    : {len(population[0].genes)}")
    print(f"  (one gene per course: {len(courses)} courses)")
    print(f"  Possible combos    : {len(rooms)**len(courses)} room combos"
          f" × {len(time_slots)**len(courses)} slot combos"
          f" = {(len(rooms)*len(time_slots))**len(courses):,} total timetables")
    print(f"\n  → The GA must search this space intelligently.")
    print(f"    Brute force is impossible. That's why we use a GA.")
