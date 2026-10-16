"""Lesson scenes. Each class is one clip; it narrates itself with self.say("… [words] …", animation).

Render one to look at it:   python -m manimgx inspect scenes.py KeyIdea
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manimgx as m  # noqa: E402

from voxim import Kit, Scene  # noqa: E402
from film import BRAND, VOICE  # noqa: E402

K = Kit(BRAND)


class Base(Scene):
    voice = VOICE


class Intro(Base):
    def construct(self):
        card = K.title_card("Lesson title", "What you will be able to do by the end", kicker="Grade 7 science")
        self.say("[Today] we're going to learn something new.", m.FadeIn(card, shift=m.UP * 0.3))
        self.wait(0.5)


class KeyIdea(Base):
    def construct(self):
        h = K.top_heading("The key idea", "One idea, shown step by step")
        g, rows = K.steps(["First thing that happens", "Second thing", "What it leads to"])
        g.next_to(h, m.DOWN, buff=0.7).align_to(h, m.LEFT)
        self.add(h)
        self.say("[First] this happens. [Then] this. [And so] we get this.",
                 m.FadeIn(rows[0], shift=m.RIGHT * 0.3), m.FadeIn(rows[1], shift=m.RIGHT * 0.3),
                 m.FadeIn(rows[2], shift=m.RIGHT * 0.3))
        self.wait(0.5)


class Check(Base):
    def construct(self):
        card, timer = K.question("Can you explain the key idea in your own words?", seconds=5)
        self.say("[Pause the video] and try this.", m.FadeIn(card, shift=m.UP * 0.3))
        self.play(timer)
        self.wait(0.3)
