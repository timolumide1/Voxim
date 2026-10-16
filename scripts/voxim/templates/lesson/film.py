"""Lesson film settings. Rename things freely; `voxim build .` reads this file."""
from voxim import Brand, narrator, manim

TITLE = "Lesson title"
MODE = "lesson"                       # writes clips/ and guide.md; captions burned in
AUDIENCE = "Grade 7 science"          # shown in guide.md
OBJECTIVES = ["Students can explain …"]
SOURCE = "Teacher's notes"           # what the film was built from

BRAND = Brand(name=TITLE, accent="#2563eb", accent2="#c2410c", soft="#e8f0fe")   # or Brand.dark(...)
VOICE = narrator("af_heart", speed=0.95)    # slower is easier for learners; `voxim voices` lists more
MUSIC = "none"                        # "pad" for a soft synthesised bed, or a path to an audio file

FILM = [
    manim("Intro", chapter="What we'll learn", use="Open the lesson"),
    manim("KeyIdea", chapter="The key idea", use="After the warm-up discussion"),
    manim("Check", use="Before independent practice"),
]
