# =============================================================================
# data.py — The Foundation of the Timetable Scheduler
# =============================================================================
# This file does ONE job: define and store all the "raw ingredients" the GA
# needs to build a timetable. Think of it as your database.
#
# It contains 4 building blocks:
#   1. TimeSlot  — when a class can happen
#   2. Room      — where a class can happen
#   3. Instructor — who teaches
#   4. Course    — what is being taught (links to instructor + students)
#
# Nothing is scheduled here. No logic. No algorithm.
# Just clean data definitions — ready to be used by every other file.
# =============================================================================


# -----------------------------------------------------------------------------
# BUILDING BLOCK 1: TimeSlot
# -----------------------------------------------------------------------------
# A TimeSlot represents a single period in the week.
# Every class must be assigned to exactly one TimeSlot.
#
# Why a class instead of a plain list?
#   → Using a class lets us attach a readable name (e.g. "Mon 9-10am") to
#     each slot. Later when printing the timetable, you'll see real labels
#     instead of confusing numbers like slot[0] or slot[2].

class TimeSlot:
    def __init__(self, slot_id, day, time):
        self.slot_id = slot_id   # e.g. "TS1" — used as a unique key
        self.day     = day       # e.g. "Monday"
        self.time    = time      # e.g. "9:00–10:00 AM"

    def __repr__(self):
        # __repr__ controls what prints when you do print(timeslot)
        # Without this you'd see something useless like <TimeSlot object at 0x...>
        return f"{self.day} {self.time}"


# -----------------------------------------------------------------------------
# BUILDING BLOCK 2: Room
# -----------------------------------------------------------------------------
# A Room has a capacity. This matters for soft constraints:
#   → If 45 students enrol in a course but the room only fits 30, that's a
#     soft constraint violation (penalty +2 in your fitness function).

class Room:
    def __init__(self, room_id, capacity):
        self.room_id  = room_id    # e.g. "R1"
        self.capacity = capacity   # maximum number of students it can hold

    def __repr__(self):
        return f"Room {self.room_id} (cap: {self.capacity})"


# -----------------------------------------------------------------------------
# BUILDING BLOCK 3: Instructor
# -----------------------------------------------------------------------------
# An Instructor can only teach ONE course at a time.
# This is one of your hard constraints:
#   → If T1 is assigned to both C1 and C4 in the same time slot → clash → +10 penalty.

class Instructor:
    def __init__(self, instructor_id, name):
        self.instructor_id = instructor_id   # e.g. "T1"
        self.name          = name            # e.g. "Umber Nisar"

    def __repr__(self):
        return self.name


# -----------------------------------------------------------------------------
# BUILDING BLOCK 4: Course
# -----------------------------------------------------------------------------
# A Course ties everything together — it knows:
#   - which instructor teaches it
#   - which students attend it (as a list of student IDs)
#
# The student list is critical for detecting student conflicts:
#   → If student S20 is enrolled in both C1 and C4, they can't be scheduled
#     at the same time slot.

class Course:
    def __init__(self, course_id, name, instructor, students):
        self.course_id  = course_id    # e.g. "C1"
        self.name       = name         # e.g. "Data Structures"
        self.instructor = instructor   # an Instructor object (not just a string)
        self.students   = students     # list of student IDs e.g. ["S1", "S2", ...]

    def __repr__(self):
        return f"{self.course_id}: {self.name}"


# =============================================================================
# SAMPLE DATASET
# =============================================================================
# This is the exact dataset from your literature review document.
# When you get real data from Miss Ayesha Khan, you will ONLY edit this
# section — the rest of the project stays exactly the same.
# =============================================================================

# --- Step 1: Define Time Slots ------------------------------------------------
# 4 slots across Monday and Tuesday (from your data description doc)

time_slots = [
    TimeSlot("TS1", "Monday",  "9:00–10:00 AM"),
    TimeSlot("TS2", "Monday",  "10:00–11:00 AM"),
    TimeSlot("TS3", "Tuesday", "9:00–10:00 AM"),
    TimeSlot("TS4", "Tuesday", "10:00–11:00 AM"),
]

# --- Step 2: Define Rooms -----------------------------------------------------
# 3 rooms with different capacities

rooms = [
    Room("R1", capacity=50),
    Room("R2", capacity=40),
    Room("R3", capacity=30),
]

# --- Step 3: Define Instructors -----------------------------------------------
# 3 instructors — note T1 (Umber Nisar) teaches TWO courses (C1 and C4).
# This is intentional — it's what makes the scheduling hard!

instructors = {
    "T1": Instructor("T1", "Umber Nisar"),
    "T2": Instructor("T2", "Ayesha Khan"),
    "T3": Instructor("T3", "Aasia Khanum"),
}

# --- Step 4: Define Courses ---------------------------------------------------
# Students are stored as ranges converted to lists.
# e.g. "S1–S30" → ["S1", "S2", ..., "S30"]
# The overlap between student lists is what causes student conflicts.
#
# IMPORTANT OVERLAPS in this dataset (these create hard constraint challenges):
#   C1 has S1–S30
#   C2 has S10–S40   ← S10–S30 overlap with C1 (students in both!)
#   C3 has S5–S25    ← S5–S25 overlap with C1 and C2
#   C4 has S20–S50   ← S20–S30 overlap with C1, S20–S25 with C3
#
# AND C1 and C4 share the same instructor (T1) — double conflict risk!

courses = [
    Course("C1", "Data Structures",  instructors["T1"],
           [f"S{i}" for i in range(1,  31)]),   # S1–S30

    Course("C2", "AI Fundamentals",  instructors["T2"],
           [f"S{i}" for i in range(10, 41)]),   # S10–S40

    Course("C3", "Databases",        instructors["T3"],
           [f"S{i}" for i in range(5,  26)]),   # S5–S25

    Course("C4", "Operating Systems",instructors["T1"],
           [f"S{i}" for i in range(20, 51)]),   # S20–S50
]


# =============================================================================
# QUICK SELF-TEST
# =============================================================================
# Run this file directly ("python data.py") to verify everything loaded
# correctly. You should see all 4 building blocks printed clearly.
# This will NOT run when other files import data.py (that's what if __name__
# guards are for).
# =============================================================================

if __name__ == "__main__":

    print("=" * 50)
    print("TIME SLOTS")
    print("=" * 50)
    for ts in time_slots:
        print(f"  {ts.slot_id} → {ts}")

    print("\n" + "=" * 50)
    print("ROOMS")
    print("=" * 50)
    for r in rooms:
        print(f"  {r.room_id} → capacity: {r.capacity}")

    print("\n" + "=" * 50)
    print("INSTRUCTORS")
    print("=" * 50)
    for key, inst in instructors.items():
        print(f"  {inst.instructor_id} → {inst.name}")

    print("\n" + "=" * 50)
    print("COURSES")
    print("=" * 50)
    for c in courses:
        print(f"  {c.course_id} → {c.name}")
        print(f"    Instructor : {c.instructor.name}")
        print(f"    Students   : {c.students[0]} to {c.students[-1]}"
              f" ({len(c.students)} total)")

    print("\n" + "=" * 50)
    print("STUDENT OVERLAPS (potential conflicts)")
    print("=" * 50)
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            c1, c2 = courses[i], courses[j]
            overlap = set(c1.students) & set(c2.students)
            if overlap:
                print(f"  {c1.course_id} & {c2.course_id} share"
                      f" {len(overlap)} students → conflict risk if same slot!")
