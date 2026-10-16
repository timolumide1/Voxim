---
name: voxim
description: Make narrated, captioned explainer videos with animated diagrams (ManimGX) and an offline voice. Use when a teacher shares a lesson plan, teaching notes or a topic and wants instructional videos or animations for the parts that need a visual, or when someone wants an explainer, product video, or narrated website walkthrough. Produces short per-concept clips, a full film, captions and a teacher's guide.
---

# Voxim

Turns teaching notes (or a product) into narrated, captioned animation. Everything runs locally:
ManimGX draws and times the animation, Kokoro speaks the narration offline, ffmpeg assembles it.
The person only installs this skill; the first run installs the rest.

Two modes, same tools:

- **Lesson mode** (default): read a teacher's notes, find the parts of the lesson a visual would
  genuinely help, and make one short clip per part, plus the whole set joined as one film and a
  guide saying where each clip goes in the lesson. Read `references/lesson-mode.md` before planning.
- **Product mode**: an explainer for a product or website, optionally with a recorded, narrated
  screen demo, plus YouTube details. Read `references/product-mode.md`.

## 0. Install (once per machine)

Look for the command first: `~/.voxim/venv/bin/voxim` (Windows:
`%USERPROFILE%\.voxim\venv\Scripts\voxim.exe`). If it's missing, run the installer from
this skill's folder; it creates a private Python 3.13 environment, installs everything, downloads the
voice model (~340 MB) and runs a self-test:

```bash
bash <skill-dir>/scripts/install.sh            # add --screen for website demos (installs a browser)
# Windows: powershell -ExecutionPolicy Bypass -File <skill-dir>\scripts\install.ps1
```

Below, `voxim` means that full path. Installing takes a few minutes; tell the person once, then carry on.

## 1. Understand the material

Read everything the person gave: lesson plan, notes, slides, worksheet, the chat itself. For a lesson,
pull out: the class (age/grade, subject), the learning objectives, the order of the lesson, key
vocabulary, the misconceptions the teacher mentions (or that are well known for the topic), and the
teacher's own words and examples. The teacher's content is the source of truth: don't add facts that
aren't in their notes unless they're standard and needed, and list anything you added in the guide.

## 2. Plan the visuals (lesson mode: the visual audit)

Go through the lesson part by part and decide, for each, whether a visual earns its place. Use the
rubric in `references/lesson-mode.md`: processes, change over time, spatial relationships, hidden or
invisible things, scale, cause and effect, quantities and graphs, step-by-step working, and
misconceptions are strong candidates; logistics, routines, discussion prompts and plain definitions
usually are not. Write `plan.md` in the project folder: a table of every lesson part with
*visual? / why / what the viewer sees / clip length / where it plays in the lesson*.

If the person is around, show them the plan (a short summary of which parts get clips and why) and
ask whether to go ahead. Rendering is the slow part, so the plan is the cheap place to change course.
If they're away, go ahead with your best reading and say so at the top of the guide.

## 3. Make the project

```bash
voxim new lesson <project-dir>      # or: voxim new product <project-dir>
```

That gives a working `film.py` (settings and running order) and `scenes.py` (one class per clip).
Edit them:

- `film.py`: TITLE, AUDIENCE, OBJECTIVES, BRAND colours, VOICE, and FILM: one `manim("ClassName",
  chapter=..., use="where it plays in the lesson")` per clip, in lesson order.
- `scenes.py`: write each clip. Narrate with `self.say("… [words] …", animation, …)`: each bracketed
  span starts one animation as those words are spoken. Use the Kit helpers (`K.steps`, `K.cycle`,
  `K.callout`, `K.compare`, `K.timeline`, `K.definition`, `K.misconception`, `K.question`,
  `K.summary`, `K.math`, `K.axes`, `K.hbars`, `K.count_up`) and plain ManimGX (Axes, MathTex, shapes, updaters, 3D).
  Patterns for common teaching visuals are in `references/scene-cookbook.md`.

Writing rules that matter most (details in `references/lesson-mode.md`):
- One idea per clip, 30–120 seconds. Narration at the class's reading level, in short sentences.
- The picture carries the idea; on-screen text is labels and key words, not the narration repeated.
- Reveal things as they're spoken about, in the order the narration mentions them.
- Keep content inside x ±6.4 and y −2.6 to +3.4: burned-in captions cover the strip below y = −2.6.
  Watch for things that move into it (an orbit's lowest point, a falling object).
- End each clip on a complete, readable frame: it's the frame the class sees when the teacher pauses.

## 4. Look before building

Inspect every scene as you write it, and fix what the report and the storyboard show:

```bash
cd <project-dir> && ~/.voxim/venv/bin/python -m manimgx inspect scenes.py ClassName
```

It prints the timeline and layout problems (overlaps, text off-frame) and writes
`ClassName.storyboard.png`. Open the storyboard image and look at it. Fix overlaps, cut-off
text and crowding before building.

## 5. Build and check

```bash
voxim build <project-dir>      # re-renders only scenes whose code changed
voxim check <project-dir>      # contact sheet of every clip's middle and end, audio report
```

Open `out/check.png` and look at every frame. Loudness should be about −14 LUFS. The only silent
gaps should be intended pauses (`K.question` timers). Fix and rebuild until it's clean.

Outputs in `<project-dir>/out/`:
- `clips/01-Name.mp4` … one per concept, captions burned in, plus `.srt` files
- `film.mp4`: all clips joined with short crossfades; `captions.srt`
- `guide.md` (lesson): each clip, its length, and where it fits in the lesson
- `youtube.md` (product): title, description with chapters, upload notes

## 6. Deliver

Send the clips, the film and the guide. In the reply: which parts of the lesson got a visual and
why, in a sentence or two, and anything you added beyond the teacher's notes. Don't recap the
build steps.

## Good to know

- The voice: `VOICE = narrator("af_heart", speed=0.95)` in film.py. American, British, Spanish,
  French, Hindi, Italian, Portuguese, Japanese and Mandarin voices exist; `voxim voices` lists them,
  `voxim say "text" --voice bf_emma` writes a sample. Spell out what a voice would misread
  ("H two O", "twenty-nine and a half days"); the captions use the same words, so use
  `CAPTION_TEXT` in film.py to map them back ("H₂O").
- Rendering takes roughly 5–30 seconds per scene. Speech is cached in `voice/`, so re-renders are faster.
- Video files are big. If the disk fills up, delete `<project>/build/*.norm.mov` and `*.mp4` there,
  and never leave a stray ffmpeg running (`references/troubleshooting.md`).
- Captions are burned in for lesson mode (`BURN_CAPTIONS = False` in film.py to turn off), and are
  always also written as `.srt` files.
