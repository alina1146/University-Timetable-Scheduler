# =============================================================================
# visualize.py — See the Algorithm Work
# =============================================================================
# This file does two things:
#
#   1. FITNESS GRAPH — plots best and average fitness across generations
#      so you can literally SEE the algorithm getting smarter over time
#
#   2. TIMETABLE TABLE — prints the final best timetable in a clean,
#      readable grid organized by day and time slot
#
# This is your DEMO file. When you present to your instructor, you run
# this file and show:
#   "Look — generation 0 is messy. By generation 30 it's perfect."
#   "Here is the final timetable the algorithm produced."
#
# LIBRARY NEEDED:
#   matplotlib — for drawing the graph
#   Install it once by running:  pip install matplotlib
# =============================================================================

import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from ga   import run_ga
from data import time_slots, rooms


# =============================================================================
# PART 1 — FITNESS GRAPH
# =============================================================================
# This function takes the history list from run_ga() and plots two lines:
#
#   BLUE LINE  — best fitness each generation  (the champion of each round)
#   ORANGE LINE — average fitness each generation (how the whole population is doing)
#
# What you should see on the graph:
#   → Both lines start low (near 0) — the random population is bad
#   → Both lines climb upward — the GA is improving timetables
#   → The blue line jumps ahead of orange — the best solutions lead the pack
#   → Eventually blue hits 1.0 — perfect timetable found!
#
# The gap between blue and orange tells you about DIVERSITY:
#   Small gap = population is converging (everyone is similar)
#   Large gap = still lots of variety (healthy exploration)

def plot_fitness(history, title="GA Fitness Over Generations"):
    """
    Draw the fitness graph from the history list returned by run_ga().
    Saves as 'fitness_graph.png' AND displays it on screen.
    """
    generations  = [h["generation"]   for h in history]
    best_fitness = [h["best_fitness"]  for h in history]
    avg_fitness  = [h["avg_fitness"]   for h in history]

    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot the two lines
    ax.plot(generations, best_fitness,
            color="#1F77B4", linewidth=2.5, label="Best Fitness",    zorder=3)
    ax.plot(generations, avg_fitness,
            color="#FF7F0E", linewidth=1.5, label="Average Fitness",
            linestyle="--", alpha=0.8, zorder=2)

    # Shade the area between best and average — shows how spread the population is
    ax.fill_between(generations, avg_fitness, best_fitness,
                    alpha=0.15, color="#1F77B4", label="Population Spread")

    # Mark the point where best fitness first hit 1.0 (if it did)
    perfect_gen = next((h["generation"] for h in history if h["best_fitness"] >= 1.0), None)
    if perfect_gen is not None:
        ax.axvline(x=perfect_gen, color="green", linewidth=1.5,
                   linestyle=":", alpha=0.8)
        ax.annotate(f"  Perfect at\n  gen {perfect_gen}",
                    xy=(perfect_gen, 1.0),
                    xytext=(perfect_gen + max(1, len(history) * 0.05), 0.85),
                    fontsize=9, color="green",
                    arrowprops=dict(arrowstyle="->", color="green", lw=1.2))

    # Formatting
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Generation", fontsize=11)
    ax.set_ylabel("Fitness Score  (1.0 = perfect)", fontsize=11)
    ax.set_ylim(-0.05, 1.10)
    ax.set_xlim(left=0)
    ax.axhline(y=1.0, color="green", linewidth=1.0, linestyle="--", alpha=0.5)
    ax.legend(fontsize=10, loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig("fitness_graph.png", dpi=150, bbox_inches="tight")
    print("  Graph saved as: fitness_graph.png")
    plt.show()


# =============================================================================
# PART 2 — TIMETABLE GRID
# =============================================================================
# This function takes the best chromosome and prints it as a proper timetable
# grid — the kind a university noticeboard would show.
#
# FORMAT:
#   Rows    = Time Slots  (e.g. 9–10am, 10–11am)
#   Columns = Days        (Monday, Tuesday, ...)
#   Cells   = Course assigned to that slot (or "—" if empty)
#
# Example output:
#   ┌─────────────┬─────────────────────────┬─────────────────────────┐
#   │             │ Monday                  │ Tuesday                 │
#   ├─────────────┼─────────────────────────┼─────────────────────────┤
#   │ 9:00–10:00  │ C2: AI Fundamentals     │ C4: Operating Systems   │
#   │             │ Room R2 | T2            │ Room R1 | T1            │
#   ├─────────────┼─────────────────────────┼─────────────────────────┤
#   │ 10:00–11:00 │ C1: Data Structures     │ C3: Databases           │
#   │             │ Room R1 | T1            │ Room R3 | T3            │
#   └─────────────┴─────────────────────────┴─────────────────────────┘

def print_timetable(chromosome):
    """
    Print the timetable as a readable grid in the terminal.
    """
    # Build a lookup: (day, time) → gene
    # This lets us quickly find what's scheduled at any slot
    schedule = {}
    for gene in chromosome.genes:
        key = (gene.time_slot.day, gene.time_slot.time)
        schedule[key] = gene

    # Collect unique days and times (preserve order from data.py)
    days  = list(dict.fromkeys(ts.day  for ts in time_slots))
    times = list(dict.fromkeys(ts.time for ts in time_slots))

    # Column widths
    TIME_W = 14
    DAY_W  = 28

    # ── Header ───────────────────────────────────────────────────────
    print("\n" + "=" * (TIME_W + DAY_W * len(days) + len(days) + 1))
    print("  FINAL TIMETABLE")
    print("=" * (TIME_W + DAY_W * len(days) + len(days) + 1))

    # Top border
    top = "┌" + "─" * TIME_W
    for _ in days:
        top += "┬" + "─" * DAY_W
    print(top + "┐")

    # Day headers
    header = "│" + " " * TIME_W
    for day in days:
        header += "│" + f" {day}".ljust(DAY_W)
    print(header + "│")

    # Separator after header
    sep = "├" + "─" * TIME_W
    for _ in days:
        sep += "┼" + "─" * DAY_W
    print(sep + "┤")

    # ── Rows (one per time slot) ──────────────────────────────────────
    for i, time in enumerate(times):
        # Row 1: time label + course name
        row1 = "│" + f" {time}".ljust(TIME_W)
        # Row 2: blank + room and instructor
        row2 = "│" + " " * TIME_W

        for day in days:
            gene = schedule.get((day, time))
            if gene:
                course_text = f" {gene.course.course_id}: {gene.course.name}"
                detail_text = f"   Room {gene.room.room_id} | {gene.course.instructor.name[:10]}"
            else:
                course_text = " —"
                detail_text = ""

            row1 += "│" + course_text.ljust(DAY_W)
            row2 += "│" + detail_text.ljust(DAY_W)

        print(row1 + "│")
        print(row2 + "│")

        # Separator between rows (or bottom border on last row)
        if i < len(times) - 1:
            mid = "├" + "─" * TIME_W
            for _ in days:
                mid += "┼" + "─" * DAY_W
            print(mid + "┤")
        else:
            bot = "└" + "─" * TIME_W
            for _ in days:
                bot += "┴" + "─" * DAY_W
            print(bot + "┘")

    # ── Summary below the grid ────────────────────────────────────────
    print(f"\n  Fitness Score : {chromosome.fitness:.4f}")
    print(f"  Total Penalty : {chromosome.penalty}")
    if chromosome.violations:
        print(f"  Violations    : {len(chromosome.violations)}")
        for v in chromosome.violations:
            print(f"    {v}")
    else:
        print(f"  Violations    : None ✅  — Perfect timetable!")


# =============================================================================
# PART 3 — MATPLOTLIB TIMETABLE (for saving as image)
# =============================================================================
# This draws the same timetable grid but as a proper image using matplotlib.
# Saves as 'timetable_final.png' — great for including in your report
# or showing in your presentation slides.

def plot_timetable(chromosome):
    """
    Draw the timetable as a colour-coded image and save as timetable_final.png
    """
    # Colour palette — one colour per course
    COLOURS = ["#AED6F1", "#A9DFBF", "#F9E79F", "#F5CBA7", "#D7BDE2", "#FADBD8"]

    # Build course → colour mapping
    course_colours = {}
    for i, gene in enumerate(chromosome.genes):
        course_colours[gene.course.course_id] = COLOURS[i % len(COLOURS)]

    # Build schedule lookup
    schedule = {}
    for gene in chromosome.genes:
        key = (gene.time_slot.day, gene.time_slot.time)
        schedule[key] = gene

    days  = list(dict.fromkeys(ts.day  for ts in time_slots))
    times = list(dict.fromkeys(ts.time for ts in time_slots))

    n_rows = len(times)
    n_cols = len(days)

    fig, ax = plt.subplots(figsize=(4 + n_cols * 3, 2 + n_rows * 1.4))
    ax.set_xlim(0, n_cols + 1)
    ax.set_ylim(0, n_rows + 1)
    ax.axis("off")

    ax.set_title("University Timetable — Best Schedule Found",
                 fontsize=14, fontweight="bold", pad=12)

    # Day column headers
    for j, day in enumerate(days):
        ax.text(j + 1.5, n_rows + 0.6, day,
                ha="center", va="center", fontsize=11,
                fontweight="bold", color="#1F4E79")

    # Time row labels
    for i, time in enumerate(times):
        ax.text(0.45, n_rows - i - 0.5, time,
                ha="right", va="center", fontsize=9, color="#555555")

    # Draw each cell
    for i, time in enumerate(times):
        for j, day in enumerate(days):
            gene  = schedule.get((day, time))
            x     = j + 1.0
            y     = n_rows - i - 1.0
            color = course_colours.get(gene.course.course_id, "#F0F0F0") if gene else "#F8F8F8"

            rect = mpatches.FancyBboxPatch(
                (x + 0.05, y + 0.05), 0.9, 0.9,
                boxstyle="round,pad=0.02",
                facecolor=color, edgecolor="#AAAAAA", linewidth=0.8
            )
            ax.add_patch(rect)

            if gene:
                ax.text(x + 0.5, y + 0.62,
                        f"{gene.course.course_id}: {gene.course.name}",
                        ha="center", va="center", fontsize=8.5, fontweight="bold")
                ax.text(x + 0.5, y + 0.35,
                        f"Room {gene.room.room_id}",
                        ha="center", va="center", fontsize=8, color="#444444")
                ax.text(x + 0.5, y + 0.15,
                        gene.course.instructor.name,
                        ha="center", va="center", fontsize=7.5, color="#666666")
            else:
                ax.text(x + 0.5, y + 0.5, "—",
                        ha="center", va="center", fontsize=12, color="#CCCCCC")

    # Legend
    legend_patches = [
        mpatches.Patch(facecolor=course_colours[g.course.course_id],
                       edgecolor="#AAAAAA",
                       label=f"{g.course.course_id}: {g.course.name}")
        for g in chromosome.genes
    ]
    ax.legend(handles=legend_patches, loc="upper center",
              bbox_to_anchor=(0.5, -0.02), ncol=len(chromosome.genes),
              fontsize=8.5, frameon=True)

    status = "✅ Perfect — No Violations" if not chromosome.violations else f"⚠ Penalty: {chromosome.penalty}"
    fig.text(0.5, -0.04, f"Fitness: {chromosome.fitness:.4f}  |  {status}",
             ha="center", fontsize=9, color="#555555")

    plt.tight_layout()
    plt.savefig("timetable_final.png", dpi=150, bbox_inches="tight")
    print("  Timetable image saved as: timetable_final.png")
    plt.show()


# =============================================================================
# MAIN — Run Everything
# =============================================================================

if __name__ == "__main__":

    # Use a seed that needs a few generations so the graph looks interesting
    # Change or remove this to get different results each run
    random.seed(7)

    print("Running Genetic Algorithm...\n")

    best, history = run_ga(
        population_size = 10,
        max_generations = 200,
        mutation_rate   = 0.05,
        crossover_rate  = 0.8,
    )

    # 1. Print timetable to terminal
    print_timetable(best)

    # 2. Draw fitness graph
    print("\nGenerating fitness graph...")
    plot_fitness(history, title="Timetable GA — Fitness Over Generations")

    # 3. Draw timetable image
    print("Generating timetable image...")
    plot_timetable(best)

    print("\nDone! Check fitness_graph.png and timetable_final.png")
