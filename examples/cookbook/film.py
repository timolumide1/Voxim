"""Cookbook check: every pattern from references/scene-cookbook.md."""
from voxim import Brand, narrator, manim

TITLE = "Scene cookbook"
MODE = "lesson"
BRAND = Brand(name=TITLE, accent="#c2410c", accent2="#2563eb", soft="#e8f0fe")
VOICE = narrator("af_heart", speed=0.95)
FILM = [manim(n) for n in ["Photosynthesis", "WaterCycle", "CellParts", "SolveLinear", "Graph", "Pressure",
                           "Timeline", "Compare", "KeyWord", "Myth", "Check", "Recap", "Cube3D"]]
