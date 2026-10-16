# Lesson mode: from teaching notes to clips

## The visual audit

Split the lesson into its parts (warm-up, each teaching point, each activity, check for
understanding, closure, homework). For every part, ask: **would a moving picture make this easier
to understand than the teacher talking, the board, or a still image?** Give it a clip only if yes.

Strong candidates: a visual earns its place when the idea is…

| The idea is… | Why a visual helps | What to show |
|---|---|---|
| A **process or sequence** (photosynthesis, long division, a bill becoming law) | Order and cause are easier to follow when steps appear one at a time | Steps revealed in order (`K.steps`), arrows carrying matter or energy along |
| A **cycle** (water, rock, cell, nitrogen cycle; a feedback loop) | A loop on a page reads as a list; motion shows the return | `K.cycle`, with something travelling round it |
| **Change over time** (erosion, population growth, a reaction rate) | Time can be compressed or slowed | A tracker driving a shape or a graph that draws itself |
| **Spatial or 3D** (Moon phases, seasons, molecule shape, cross-sections) | Hard to imagine from words; a viewpoint change is the key | Two views side by side, a camera move, a 3D object turning |
| **Invisible or too small/large/fast** (particles, forces, circuits, cells, the solar system) | Makes the hidden visible | Particles moving, force arrows, current dots, zoom across scales |
| **Cause and effect** (if X then Y; variables) | Showing one change causing another | Change one thing, watch the other respond, side by side |
| **Quantities and comparison** (data, fractions, proportions, graphs) | Size is seen faster than read | Bars, number lines, area models, a graph drawn point by point |
| **Worked steps** (solving an equation, balancing a reaction, a proof) | Each line follows from the last; the transformation is the lesson | `TransformMatchingTex` from line to line, highlight what changed |
| **A common misconception** (Earth's shadow causes phases; heavier falls faster) | Naming the wrong idea and showing why it fails changes minds | `K.misconception`, then the correct model in motion |
| **Structure and parts** (a cell, a flower, a sentence, a map) | Labels arrive one at a time, next to the part | A diagram with `K.callout` labels |

Usually not worth a clip: routines and logistics (grouping, materials, timings), discussion
prompts the class should answer themselves, homework instructions, a definition that is just
words (unless it's a key-word card at the start of a clip), anything the teacher clearly wants to
demonstrate live (a hands-on model, an experiment). Note those in the plan as "no clip" and say why.

A typical lesson yields **3 to 6 clips**. Prefer fewer, better clips over a clip for everything.
Useful extras when they fit the lesson: an opening hook (a question or a puzzling image), a short
recap (`K.summary`) and a check-for-understanding card (`K.question`) for the teacher to pause on.

## plan.md

Write it before any scene code:

```markdown
# <Lesson title>: visual plan
Class: Grade 7 science · Objective: explain why the Moon appears to change shape (MS-ESS1-1)

| # | Lesson part | Clip? | Why | What the viewer sees | Length | Plays |
|---|---|---|---|---|---|---|
| 1 | Bell ringer: sketch the Moon | no | Students' own ideas first | — | — | — |
| 2 | The Moon reflects sunlight | yes | Invisible: half is always lit | Sun lights a sphere; the lit half stays facing the Sun | 0:40 | After bell ringer |
| … |
```

Then turn each "yes" into a clip: a scene class whose `say` lines are the narration.

## Writing the narration

- **Audience.** Match the grade: short sentences, everyday words, new terms introduced once and
  then used consistently. For young learners, speak slower (`speed=0.9`).
- **One idea per clip**, 30–120 seconds. If it runs longer, split it.
- **Open with the question** the clip answers ("Why does the Moon change shape?"), end with the
  one-sentence answer.
- **Use the teacher's examples and words** from their notes; they'll be saying them in class too.
- **Spell out what a voice could misread**: numbers with units, chemical formulas, abbreviations.
- Write the text so it reads well as captions: one or two sentences per `say` call.

## Designing the picture (multimedia learning principles)

- **Coherence**: nothing decorative. Every shape is part of the explanation.
- **Signalling**: one accent colour marks what's being talked about now; dim the rest.
- **Spatial contiguity**: labels sit next to what they label (`K.callout`), never in a legend.
- **Temporal contiguity**: show a thing while it's being said (bracketed words in `say`).
- **Redundancy**: don't put the narration on screen as sentences. Use key words and labels; the
  captions already carry the words.
- **Segmenting**: short clips with a pause at the end; the teacher controls the pace.
- **Pre-training**: if the clip relies on a term, show it once (`K.definition`) before using it.
- Text at 1080p: body ≥ 26, labels ≥ 24, headings 44–60. At most ~12 words on screen at once.
- Colour is never the only signal: pair it with a label, position or shape. Keep strong contrast.

## Accuracy

The teacher's notes are the source of truth. Check each clip against them: numbers, names, order of
steps. Where you add something (a standard fact the notes assume, a common misconception), make
sure it's correct for the grade, and list it in the reply and the guide under "Added beyond the
notes". When diagrams simplify (scale of the solar system, atoms as balls), say so in the narration
once ("not to scale").

## film.py for a lesson

```python
TITLE = "Why does the Moon change shape?"
MODE = "lesson"
AUDIENCE = "Grade 7 science"
OBJECTIVES = ["Explain that the Moon reflects sunlight and half of it is always lit",
              "Use a model to explain the sequence of phases"]
SOURCE = "Ms Rivera's lesson plan, Earth & Space unit, week 3"
BRAND = Brand.dark(accent="#f5c542")          # a dark look suits space; the light default suits most topics
VOICE = narrator("af_heart", speed=0.95)
FILM = [
    manim("Hook", chapter="The question", use="Start of lesson, after the bell ringer"),
    manim("HalfLit", chapter="Half is always lit", use="Teaching point 1"),
    ...
]
```

The `use` text goes in the guide's "Where it fits in the lesson" column. Write it in the
teacher's terms ("after the lamp-and-ball model", "before the exit ticket").
