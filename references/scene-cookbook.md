# Scene cookbook

Patterns for common teaching visuals. Use `K.axes(...)` rather than bare `m.Axes`: ManimGX's default
axis numbers are white, which vanishes on a light background. Each is a complete scene; all of them render as written
(they're checked against `examples/cookbook/scenes.py`). Every scene file starts like this:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import manimgx as m
from voxim import Kit, Scene
from film import BRAND, VOICE

K = Kit(BRAND)

class Base(Scene):
    voice = VOICE
```

## How narration drives animation

`self.say(script, *animations)`: each `[bracketed span]` starts the next animation as those
words are spoken; it lasts as long as the words, or its own `run_time` if longer (the scene then
waits for it). An empty `[]` starts an animation at that point. No brackets: the animations play
during the whole line. Split long narration into several `say` calls, one or two sentences each.
`self.play(...)` runs silent animation; `self.wait(s)` holds.

Updaters make things follow a value: drive a `m.ValueTracker` and build the picture with
`m.always_redraw(lambda: ...)`, so one number (an angle, a time, a temperature) moves everything
consistently.

## A process, step by step

```python
class Photosynthesis(Base):
    def construct(self):
        h = K.top_heading("Photosynthesis", "How a leaf makes food")
        g, rows = K.steps(["Roots take in water", "Leaves take in carbon dioxide",
                           "Sunlight powers the reaction", "The plant makes glucose and gives out oxygen"])
        g.next_to(h, m.DOWN, buff=0.6).align_to(h, m.LEFT)
        self.add(h)
        self.say("[First, the roots take in water.] [The leaves take in carbon dioxide from the air.]",
                 m.FadeIn(rows[0], shift=m.RIGHT * 0.3), m.FadeIn(rows[1], shift=m.RIGHT * 0.3))
        self.say("[Sunlight powers the reaction], [and the plant makes glucose, giving out oxygen.]",
                 m.FadeIn(rows[2], shift=m.RIGHT * 0.3), m.FadeIn(rows[3], shift=m.RIGHT * 0.3))
        self.wait(0.6)
```

## A cycle

```python
class WaterCycle(Base):
    def construct(self):
        g, nodes, arrows = K.cycle(["Evaporation", "Condensation", "Precipitation", "Collection"], radius=2.6)
        g.shift(m.DOWN * 0.3)
        self.say("[Water evaporates] from oceans and lakes.", m.FadeIn(nodes[0]))
        for i, line in enumerate(["[It condenses] into clouds.", "[It falls] as rain or snow.",
                                  "[It collects] in rivers and seas, [and the cycle starts again.]"]):
            anims = [m.AnimationGroup(m.Create(arrows[i]), m.FadeIn(nodes[i + 1]))]
            if i == 2:
                anims.append(m.Create(arrows[3]))
            self.say(line, *anims)
        self.wait(0.6)
```

## A labelled diagram

```python
class CellParts(Base):
    def construct(self):
        cell = m.Ellipse(width=6, height=3.8, fill_color=BRAND.soft, fill_opacity=1, stroke_color=BRAND.accent2, stroke_width=4)
        nucleus = m.Circle(radius=0.8, fill_color=BRAND.accent2, fill_opacity=0.8, stroke_width=0).shift(m.LEFT * 0.6)
        mito = m.Ellipse(width=1.1, height=0.5, fill_color=BRAND.accent, fill_opacity=1, stroke_width=0).shift(m.RIGHT * 1.6 + m.DOWN * 0.7)
        pic = m.VGroup(cell, nucleus, mito).shift(m.DOWN * 0.2)
        l1 = K.callout(nucleus, "Nucleus", direction=m.UP, buff=1.6)
        l2 = K.callout(mito, "Mitochondrion", direction=m.RIGHT, buff=1.0)
        l3 = K.callout(cell, "Cell membrane", direction=m.LEFT, buff=0.6)
        self.say("Here's [an animal cell].", m.FadeIn(pic))
        self.say("[The nucleus] holds the cell's instructions. [Mitochondria] release energy. "
                 "[The membrane] controls what goes in and out.", m.FadeIn(l1), m.FadeIn(l2), m.FadeIn(l3))
        self.wait(0.6)
```

## Worked steps of an equation

Write each line as a `MathTex` with the same pieces split into separate strings, so
`TransformMatchingTex` can move the pieces that stay and fade the ones that change.

```python
class SolveLinear(Base):
    def construct(self):
        lines = [K.math(r"3x + 5 = 20", 72), K.math(r"3x = 20 - 5", 72), K.math(r"3x = 15", 72), K.math(r"x = 5", 72)]
        cur = lines[0]
        self.say("[Let's solve three x plus five equals twenty.]", m.Write(cur))
        for line, said in zip(lines[1:], ["[Take five from both sides.]", "[Twenty minus five is fifteen.]",
                                          "[Divide both sides by three.] So x is five."]):
            self.say(said, m.TransformMatchingTex(cur, line))
            cur = line
        self.play(m.Circumscribe(cur, color=BRAND.accent))
        self.wait(0.6)
```

## A graph that draws itself

```python
class Graph(Base):
    def construct(self):
        ax, labels = K.axes([0, 10, 2], [0, 100, 20], x_label="Time (s)", y_label="Distance (m)")
        m.VGroup(ax, labels).move_to(m.DOWN * 0.1)
        curve = ax.plot(lambda t: t * t, x_range=[0, 10], color=BRAND.accent, stroke_width=6)
        dot = m.Dot(color=BRAND.accent).move_to(ax.c2p(0, 0))
        self.say("[Here's distance against time] for a ball rolling down a slope.", m.AnimationGroup(m.Create(ax), m.FadeIn(labels)))
        self.say("[It covers more ground every second], so the line curves upward.",
                 m.AnimationGroup(m.Create(curve, run_time=4), m.MoveAlongPath(dot, curve, run_time=4)))
        self.wait(0.6)
```

## Cause and effect with a slider

```python
class Pressure(Base):
    def construct(self):
        t = m.ValueTracker(1.0)                      # temperature, arbitrary units
        box = K.panel(5, 4).shift(m.LEFT * 2.5 + m.DOWN * 0.3)
        rng = np.random.default_rng(1)
        pts = rng.uniform([-2.2, -1.7, 0], [2.2, 1.7, 0], (18, 3)); vel = rng.normal(0, 1, (18, 3)); vel[:, 2] = 0
        dots = m.VGroup(*[m.Dot(box.get_center() + p, radius=0.09, color=BRAND.accent) for p in pts])
        def move(group, dt):
            for d, v in zip(group, vel):
                d.shift(v * dt * t.get_value() * 1.5)
                for k, half in ((0, 2.3), (1, 1.8)):
                    off = d.get_center()[k] - box.get_center()[k]
                    if abs(off) > half:
                        v[k] *= -1
                        d.shift((np.sign(off) * half - off) * (np.eye(3)[k]))
        dots.add_updater(move)
        gauge = m.always_redraw(lambda: K.num(t.get_value() * 100, size=72, suffix=" kPa").move_to([3.3, 0.2, 0]))
        label = K.kicker("Pressure").next_to([3.3, 1.0, 0], m.UP)
        self.add(box, dots, gauge, label)
        self.say("[Heat the gas], and the particles move faster.", t.animate(run_time=4).set_value(2.0))
        self.say("They hit the walls harder and more often, [so the pressure rises].", m.Indicate(gauge))
        self.wait(0.6)
```

## Timeline

```python
class Timeline(Base):
    def construct(self):
        g, line, marks = K.timeline([("1903", "First powered flight"), ("1927", "First solo Atlantic flight"),
                                     ("1947", "Faster than sound"), ("1969", "Moon landing")])
        self.say("[In just sixty-six years,]", m.Create(line))
        self.say("we went from [the first powered flight] [to crossing the Atlantic], "
                 "[breaking the sound barrier] [and landing on the Moon].",
                 *[m.FadeIn(mk, shift=m.UP * 0.2) for mk in marks])
        self.wait(0.6)
```

## Compare two things

```python
class Compare(Base):
    def construct(self):
        g, lp, rp = K.compare("Mitosis", ["One division", "Two identical cells", "Growth and repair"],
                              "Meiosis", ["Two divisions", "Four different cells", "Makes sex cells"])
        self.say("[Mitosis] makes copies for growth. [Meiosis] makes sex cells, each one different.",
                 m.FadeIn(lp, shift=m.UP * 0.2), m.FadeIn(rp, shift=m.UP * 0.2))
        self.wait(0.6)
```

## Key word, misconception, check, recap

```python
class KeyWord(Base):
    def construct(self):
        card = K.definition("Photosynthesis", "How plants use light to turn water and carbon dioxide into food.")
        self.say("[Photosynthesis] is how plants make their own food.", m.FadeIn(card, shift=m.UP * 0.2))
        self.wait(0.6)

class Myth(Base):
    def construct(self):
        wg, strike, rg = K.misconception("Heavier things fall faster.",
                                         "Without air resistance, everything falls at the same rate.")
        self.say("[You might think heavier things fall faster.] [They don't.]", m.FadeIn(wg), m.Create(strike))
        self.say("[Without air in the way, a hammer and a feather land together.]", m.FadeIn(rg))
        self.wait(0.6)

class Check(Base):
    def construct(self):
        card, timer = K.question("Which falls faster on the Moon: a hammer or a feather?", seconds=5)
        self.say("[Pause the video] and decide.", m.FadeIn(card))
        self.play(timer)                       # a silent pause the teacher can stop on
        self.wait(0.3)

class Recap(Base):
    def construct(self):
        g, rows = K.summary("What we learned", ["Plants make food from light", "They need water and CO₂",
                                                "They give out oxygen"])
        self.say("[So,] [plants make food from light,] [using water and carbon dioxide,] [and give out oxygen.]",
                 m.FadeIn(g[0]), *[m.FadeIn(r, shift=m.RIGHT * 0.2) for r in rows])
        self.wait(0.8)
```

## 3D

```python
class Cube3D(m.ThreeDScene):
    voice = VOICE
    def construct(self):
        self.set_camera_orientation(phi=65 * m.DEGREES, theta=-45 * m.DEGREES)
        cube = m.Cube(side_length=2.5, fill_color=BRAND.accent2, fill_opacity=0.7, stroke_color=BRAND.ink, stroke_width=2)
        self.say("[A cube has six faces], all of them squares.", m.Create(cube))
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(3)
```

Text in a 3D scene turns with the camera unless pinned: `self.add_fixed_in_frame_mobjects(label)`.

## Tips that save time

- Build the picture once, reveal it in pieces: create everything up front, then `FadeIn` parts in
  `say` calls. Positions don't jump.
- Position with relationships (`next_to`, `arrange`, `align_to`) not raw coordinates, except for
  the main layout grid.
- Pass `color=` hex strings from BRAND so everything matches; dim what isn't being discussed with
  `.animate.set_opacity(0.3)`.
- For anything numeric or physical, compute positions from the real relationship (as the Moon
  example computes each phase from the orbit angle). It stays correct at every frame.
- `self.clear_all()` fades everything out between parts of one clip.
