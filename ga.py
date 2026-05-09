# =============================================================================
# ga.py — The Genetic Algorithm Engine
# =============================================================================
# This file is the heart of the project. It takes a population of random
# timetables and EVOLVES them over many generations until it finds one
# with zero (or very few) clashes.
#
# HOW A GENETIC ALGORITHM WORKS — THE BIG PICTURE:
#
#   Generation 0:  Create 10 random timetables (mostly terrible)
#   Generation 1:  Pick the best ones → mix them → make 10 new ones
#   Generation 2:  Pick the best ones → mix them → make 10 new ones
#   ...repeat...
#   Generation N:  One timetable reaches fitness = 1.0 → DONE!
#
# The 4 operations that make this work:
#
#   1. SELECTION   — pick the better timetables (survival of the fittest)
#   2. CROSSOVER   — mix two timetables to make a new one
#   3. MUTATION    — randomly tweak one small thing (prevents getting stuck)
#   4. ELITISM     — always keep the best timetable (never go backwards)
#
# Think of it like breeding: you pick the best parents, they have children
# that inherit traits from both, and sometimes a child has a random mutation.
# Over many generations, the population gets better and better.
# =============================================================================

import random
from chromosome import Chromosome, Gene, create_population
from fitness    import calculate_fitness
from data       import rooms, time_slots


# =============================================================================
# STEP 1 — SELECTION
# =============================================================================
# Selection decides which timetables get to "reproduce" (be used as parents).
# We use TOURNAMENT SELECTION — one of the most common and reliable methods.
#
# HOW TOURNAMENT SELECTION WORKS:
#   - Pick 3 random chromosomes from the population
#   - Compare their fitness scores
#   - The one with the highest fitness WINS and becomes a parent
#
# Why tournament and not just "pick the top 2"?
#   → If we always picked the absolute best, all children would come from
#     the same 1-2 parents. The population would lose diversity very fast
#     and get stuck in a local optimum (a "good enough" but not perfect solution).
#   → Tournament adds a bit of luck — weaker chromosomes can occasionally
#     win, keeping variety in the population.
#
# Visual example:
#   Pool: [fitness=0.09, fitness=0.33, fitness=0.50, fitness=0.20, ...]
#   Pick 3 random: [0.09, 0.50, 0.20]
#   Winner: 0.50 → this chromosome becomes a parent

def tournament_selection(population, tournament_size=3):
    """
    Randomly pick `tournament_size` chromosomes and return the best one.
    Called twice to get two parents for crossover.
    """
    # Randomly grab a small group from the population
    competitors = random.sample(population, tournament_size)

    # Return the one with the highest fitness score
    winner = max(competitors, key=lambda chrom: chrom.fitness)
    return winner


# =============================================================================
# STEP 2 — CROSSOVER
# =============================================================================
# Crossover takes two parent timetables and combines them to make a child.
# We use SINGLE-POINT CROSSOVER — the simplest and most intuitive method.
#
# HOW SINGLE-POINT CROSSOVER WORKS:
#   - Pick a random "cut point" somewhere in the gene list
#   - Child takes genes BEFORE the cut point from Parent A
#   - Child takes genes AFTER  the cut point from Parent B
#
# Visual example with 4 genes (courses C1, C2, C3, C4):
#
#   Parent A: [C1→R1,TS1]  [C2→R2,TS2]  [C3→R1,TS3]  [C4→R2,TS4]
#   Parent B: [C1→R3,TS2]  [C2→R1,TS4]  [C3→R2,TS1]  [C4→R3,TS3]
#   Cut at index 2:
#   Child:    [C1→R1,TS1]  [C2→R2,TS2] | [C3→R2,TS1]  [C4→R3,TS3]
#              ← from Parent A →        | ← from Parent B →
#
# Why does this help?
#   If Parent A has a great schedule for C1 and C2 but bad for C3 and C4,
#   and Parent B is the opposite — the child inherits the best of both!
#
# CROSSOVER RATE (0.8):
#   80% of the time we do crossover.
#   20% of the time we just clone one parent unchanged.
#   This ensures some parents survive directly to the next generation.

def crossover(parent_a, parent_b, crossover_rate=0.8):
    """
    Combine two parent chromosomes to produce one child chromosome.
    """
    # 20% chance: skip crossover, just clone parent_a
    if random.random() > crossover_rate:
        child_genes = [
            Gene(g.course, g.room, g.time_slot)
            for g in parent_a.genes
        ]
        return Chromosome(child_genes)

    # Pick a random cut point (not at the very start or very end)
    num_genes = len(parent_a.genes)
    cut_point = random.randint(1, num_genes - 1)

    # Take genes before cut from parent_a, genes from cut onward from parent_b
    child_genes = []
    for i in range(num_genes):
        if i < cut_point:
            source = parent_a.genes[i]
        else:
            source = parent_b.genes[i]

        # Create a fresh Gene object (don't share references with parents)
        child_genes.append(Gene(source.course, source.room, source.time_slot))

    return Chromosome(child_genes)


# =============================================================================
# STEP 3 — MUTATION
# =============================================================================
# Mutation makes a small random change to a chromosome.
# It is the GA's way of exploring new territory.
#
# WHY IS MUTATION NECESSARY?
#   Without mutation, the GA can only combine what already exists in the
#   population. If every timetable in the population has C1 in Room R1,
#   crossover will never produce a child with C1 in Room R2 or R3.
#   Mutation breaks out of this trap.
#
# HOW OUR MUTATION WORKS:
#   For each gene in the chromosome:
#     → Roll a random number between 0 and 1
#     → If it's below the mutation_rate (5%), randomly reassign that gene's
#       room OR time slot (50/50 chance of which one changes)
#
# MUTATION RATE (0.05 = 5%):
#   Too high (e.g. 50%) → the algorithm becomes random search, not evolution
#   Too low  (e.g. 0%)  → the algorithm gets stuck, no new ideas
#   5% is the standard sweet spot for most GA problems
#
# Visual example:
#   Before: C3 → R1, Monday 9am
#   Mutation fires on this gene → randomly pick new room
#   After:  C3 → R3, Monday 9am   ← only the room changed

def mutate(chromosome, mutation_rate=0.05):
    """
    Randomly alter each gene with probability = mutation_rate.
    Returns the mutated chromosome (modified in place).
    """
    for gene in chromosome.genes:
        if random.random() < mutation_rate:
            # 50/50: mutate the room OR the time slot (not both at once)
            if random.random() < 0.5:
                gene.room       = random.choice(rooms)
            else:
                gene.time_slot  = random.choice(time_slots)

    return chromosome


# =============================================================================
# STEP 4 — ELITISM
# =============================================================================
# Elitism means: always copy the single best chromosome from the current
# generation directly into the next generation, unchanged.
#
# WHY IS THIS IMPORTANT?
#   Without elitism, it's possible that crossover or mutation accidentally
#   destroys the best timetable we've found so far. With elitism, the best
#   solution is always preserved — we can only ever stay the same or improve.
#
# This is a very small change that makes a big difference in stability.
# Most real-world GA implementations use elitism.

def get_elite(population):
    """Return the single best chromosome from the population."""
    return max(population, key=lambda chrom: chrom.fitness)


# =============================================================================
# THE MAIN GA LOOP
# =============================================================================
# This function runs the entire Genetic Algorithm from start to finish.
#
# PARAMETERS:
#   population_size — how many timetables in each generation (default: 10)
#   max_generations — maximum number of generations to run  (default: 200)
#   mutation_rate   — probability of mutating each gene     (default: 0.05)
#   crossover_rate  — probability of doing crossover        (default: 0.80)
#
# WHAT HAPPENS EACH GENERATION:
#   1. Score every chromosome using the fitness function
#   2. Check if the best one is perfect (fitness = 1.0) → stop early if yes
#   3. Save the elite (best chromosome) for next generation
#   4. Build a new population:
#        a. Add the elite directly (elitism)
#        b. For remaining slots: select 2 parents → crossover → mutate → add child
#   5. Replace old population with new population
#   6. Repeat
#
# RETURNS:
#   best_chromosome  — the best timetable found
#   history          — list of (generation, best_fitness, avg_fitness) for graphing

def run_ga(population_size=10, max_generations=200,
           mutation_rate=0.05, crossover_rate=0.8):

    print("=" * 60)
    print("GENETIC ALGORITHM — University Timetable Scheduler")
    print("=" * 60)
    print(f"  Population size : {population_size}")
    print(f"  Max generations : {max_generations}")
    print(f"  Mutation rate   : {mutation_rate * 100:.0f}%")
    print(f"  Crossover rate  : {crossover_rate * 100:.0f}%")
    print("=" * 60)

    # ── Initialise ────────────────────────────────────────────────────
    # Create the first generation of random timetables
    population = create_population(population_size)

    # Score every chromosome in the initial population
    for chrom in population:
        calculate_fitness(chrom)

    # This list records fitness history for every generation (used by visualize.py)
    history = []

    # ── Generation Loop ───────────────────────────────────────────────
    for generation in range(max_generations):

        # Step 1: Find the best and average fitness this generation
        best        = get_elite(population)
        avg_fitness = sum(c.fitness for c in population) / len(population)

        # Record for history
        history.append({
            "generation"  : generation,
            "best_fitness": best.fitness,
            "avg_fitness" : avg_fitness,
            "best_penalty": best.penalty,
        })

        # Print progress every 10 generations (and always the first/last)
        if generation % 10 == 0 or best.fitness == 1.0:
            print(f"  Gen {generation:>4} | "
                  f"Best Fitness: {best.fitness:.4f} | "
                  f"Avg: {avg_fitness:.4f} | "
                  f"Penalty: {best.penalty}")

        # Step 2: Early stopping — if we found a perfect timetable, stop now
        if best.fitness == 1.0:
            print(f"\n  ✅ Perfect timetable found at generation {generation}!")
            break

        # Step 3: Build the next generation
        next_population = []

        # ELITISM: carry the best chromosome forward unchanged
        elite_copy_genes = [
            Gene(g.course, g.room, g.time_slot) for g in best.genes
        ]
        elite_copy = Chromosome(elite_copy_genes)
        elite_copy.fitness = best.fitness
        elite_copy.penalty = best.penalty
        elite_copy.violations = best.violations
        next_population.append(elite_copy)

        # Fill the rest of the population with children
        while len(next_population) < population_size:

            # Select two parents using tournament selection
            parent_a = tournament_selection(population)
            parent_b = tournament_selection(population)

            # Crossover: combine parents to make a child
            child = crossover(parent_a, parent_b, crossover_rate)

            # Mutation: randomly tweak the child
            child = mutate(child, mutation_rate)

            # Score the child
            calculate_fitness(child)

            # Add to next generation
            next_population.append(child)

        # Replace old population with new one
        population = next_population

    # ── Final Result ──────────────────────────────────────────────────
    # Score one final time and return the best
    for chrom in population:
        calculate_fitness(chrom)

    best_final = get_elite(population)

    print("\n" + "=" * 60)
    print("FINAL BEST TIMETABLE")
    print("=" * 60)
    for gene in best_final.genes:
        print(f"  {gene}")
    print(f"\n  Final Fitness : {best_final.fitness:.4f}")
    print(f"  Final Penalty : {best_final.penalty}")

    if best_final.violations:
        print(f"\n  Remaining violations:")
        for v in best_final.violations:
            print(f"  {v}")
    else:
        print(f"\n  No violations — perfect timetable! ✅")

    return best_final, history


# =============================================================================
# QUICK SELF-TEST
# =============================================================================
# Run: python ga.py
#
# You will watch the GA evolve in real time.
# The fitness score should climb from ~0.05 toward 1.0 across generations.
# With 4 courses and our sample data, it typically finds a perfect timetable
# within the first 50 generations.
# =============================================================================

if __name__ == "__main__":

    random.seed(42)   # remove this for different results each run

    best, history = run_ga(
        population_size = 10,
        max_generations = 200,
        mutation_rate   = 0.05,
        crossover_rate  = 0.8,
    )

    # Show how much the algorithm improved overall
    first_gen = history[0]
    last_gen  = history[-1]

    print("\n" + "=" * 60)
    print("IMPROVEMENT SUMMARY")
    print("=" * 60)
    print(f"  Generation 0   best fitness : {first_gen['best_fitness']:.4f}")
    print(f"  Final          best fitness : {last_gen['best_fitness']:.4f}")
    improvement = last_gen['best_fitness'] - first_gen['best_fitness']
    print(f"  Total improvement           : +{improvement:.4f}")
    print(f"  Generations run             : {len(history)}")
