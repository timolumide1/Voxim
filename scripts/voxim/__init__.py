"""voxim: narrated explainer and lesson videos from ManimGX scenes and screen recordings."""
from __future__ import annotations

from dataclasses import dataclass

from .design import Brand, Kit, Scene  # noqa: F401
from .voice import narrator, recorded  # noqa: F401

__version__ = "0.1.0"


@dataclass
class Seg:
    """One segment of the film, in running order.

    kind     "manim" (a scene class in scenes.py) or "screen" (steps in screens.py)
    name     the scene class name, or the screen segment's name
    chapter  a chapter title starting here (YouTube chapters, the lesson guide)
    use      lesson mode: where this clip fits in the lesson ("after the warm-up, before the lab")
    clip     also export this segment as its own clip (default True)
    """
    kind: str
    name: str
    chapter: str = ""
    use: str = ""
    clip: bool = True


def manim(name: str, chapter: str = "", use: str = "", clip: bool = True) -> Seg:
    return Seg("manim", name, chapter, use, clip)


def screen(name: str, chapter: str = "", use: str = "", clip: bool = True) -> Seg:
    return Seg("screen", name, chapter, use, clip)
