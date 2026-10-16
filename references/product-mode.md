# Product mode: an explainer with a recorded website demo

For a product, app or website: animated scenes (what it is, the problem, the numbers) plus a
narrated screen recording of the site itself, joined into one film with a music bed, captions and
YouTube upload details.

```bash
voxim setup --screen                 # once: installs Playwright's browser
voxim new product <project-dir>
voxim build <project-dir> --url http://localhost:3000
```

## film.py

```python
TITLE = "Acme Planner"
MODE = "product"                 # music bed on, captions as .srt (not burned in), youtube.md
BRAND = Brand(name="Acme Planner", accent="#c2410c", logo_svg="logo.svg", url="acmeplanner.com")
VOICE = narrator("bf_emma")
MUSIC = "pad"                    # synthesised ambient bed, ducked under the voice; or a file path; or "none"
BASE_URL = "http://localhost:3000"
URL_TEXT = "acmeplanner.com"     # shown in the browser frame's address bar
FILM = [
    manim("Title", chapter="What it is"),
    manim("Problem"),
    screen("Demo", chapter="How to use it"),
    manim("Outro", chapter="Try it"),
]
YOUTUBE = """# YouTube upload details
**Title** {title}: …
**Description** …
In this video:
{chapters}
"""
def CAPTION_TEXT(s): return s.replace("acme planner dot com", "acmeplanner.com")
```

`CLIPS = True` also writes each segment as its own clip, as in lesson mode.

## screens.py

Each step is spoken, and the recording holds on it until its line is finished:

```python
from voxim.screen import ScreenScene

Demo = [
    ScreenScene("home", "Start on the home page.", "Home", lambda d: d.go("/")),
    ScreenScene("search", "Type the role you're after.", "Search by role",
                lambda d: d.type("input[name=q]", "nurse")),
    ScreenScene("go", "Press search.", "Results", lambda d: d.click("button[type=submit]", navigates=True)),
    ScreenScene("look", "Each result shows the details that matter.", "Results",
                lambda d: (d.zoom(".result:first-child", 1.3), d.unzoom())),
]
```

The list's name matches the segment name in FILM (`screen("Demo")` → `Demo = [...]`); a film
with one screen segment can call it `SCREENS`.

Director actions: `go(path)`, `click(selector, navigates=False)`, `type(selector, text)`,
`hover(selector)`, `scroll(px)`, `zoom(selector, scale)`, `unzoom()`, `label(text)`. A cursor,
click rings and a step label are drawn over the page; the recording (1600×900) is framed in a
browser window on a background in the brand's colours.

Tips:
- Run the site locally with realistic data. Check every selector exists before building.
- Never wait for "network idle": pages that hold a connection open stall it. The director waits
  for "load" and a short settle instead.
- Keep each step's line short (one sentence); the step holds for as long as it's spoken.
- A sign-in step needs a test account; never record real personal data.

## Scenes for a product film

Typical running order: Title (logo, one-line promise) → Problem (what's hard today) → a few
scenes with the key numbers or features (`K.count_up`, `K.hbars`, `K.compare`) → a section card
(`K.section("03", "See it in action")`) → the screen demo → Outro (name and URL).

Numbers from data: load them from a JSON file in the project (`json.loads((HERE / "data.json").read_text())`)
so the film is rebuilt from fresh data with one command.
