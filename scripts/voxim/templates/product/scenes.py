import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import manimgx as m  # noqa: E402

from voxim import Kit, Scene  # noqa: E402
from film import BRAND, VOICE  # noqa: E402

K = Kit(BRAND)


class Base(Scene):
    voice = VOICE


class Title(Base):
    def construct(self):
        logo = K.logo(1.4)
        name = K.head(BRAND.name, size=100, weight="ULTRABOLD")
        lockup = m.VGroup(logo, name).arrange(m.RIGHT, buff=0.45).shift(m.UP * 0.4)
        tag = K.body("What it does, in one line", size=36).next_to(lockup, m.DOWN, buff=0.5)
        self.say("[Meet the product]. [It does one useful thing] very well.",
                 m.AnimationGroup(m.DrawBorderThenFill(logo), m.FadeIn(name, shift=m.RIGHT * 0.4)),
                 m.FadeIn(tag, shift=m.UP * 0.2))
        self.wait(0.3)


class Outro(Base):
    def construct(self):
        name = K.head(BRAND.name, size=100, weight="ULTRABOLD")
        url = K.head(BRAND.url, size=48, color=BRAND.accent2).next_to(name, m.DOWN, buff=0.4)
        self.say(f"[Try it today] at {BRAND.url}.", m.AnimationGroup(m.FadeIn(name), m.FadeIn(url, shift=m.UP * 0.2)))
        self.wait(0.8)
