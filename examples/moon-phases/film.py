"""Phases of the Moon: Grade 7 lesson film, built from teacher-notes.md (see plan.md)."""
from voxim import Brand, narrator, manim

TITLE = "Phases of the Moon"
MODE = "lesson"
AUDIENCE = "Grade 7 science, Earth & Space unit (MS-ESS1-1)"
OBJECTIVES = [
    "Explain that the Moon reflects light from the Sun",
    "Explain that half the Moon is always lit, and the phase is how much of that half faces Earth",
    "Put the eight phases in order; a full cycle takes about 29.5 days",
]
SOURCE = "teacher-notes.md (lesson plan: Phases of the Moon)"
NOTES = [
    "Phases are shown as seen from the Northern Hemisphere (lit on the right while waxing).",
    "Added beyond the notes: 'not to scale' labels, and a day counter in TwoViews (from the notes' 29.5 days).",
    "Not made into clips, on purpose: the bell ringer, the lamp-and-ball activity (students should discover it), closure, exit ticket and homework.",
]

BRAND = Brand.dark(name=TITLE, accent="#f5c542", accent2="#7cb7ff")
VOICE = narrator("af_heart", speed=0.95)
MUSIC = "none"

FILM = [
    manim("MirrorLight", chapter="Moonlight is sunlight", use="After asking: does the Moon make its own light?"),
    manim("HalfLit", chapter="Half is always lit", use="Straight after MirrorLight"),
    manim("TwoViews", chapter="Why the shape changes", use="After the 'half is lit' point, before the activity"),
    manim("Shadow", chapter="It isn't Earth's shadow", use="Right after TwoViews: the misconception"),
    manim("Sequence", chapter="The eight phases", use="End of direct instruction; replay at closure"),
    manim("Check", chapter="Check for understanding", use="After the lamp-and-ball activity; pause on the question"),
]


def CAPTION_TEXT(s: str) -> str:
    return s.replace("twenty-nine and a half", "29.5")
