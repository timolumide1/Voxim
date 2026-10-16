"""Product explainer settings: animated scenes plus a recorded website demo."""
from voxim import Brand, narrator, manim, screen

TITLE = "Product name"
MODE = "product"                    # writes youtube.md; captions as a separate .srt
BRAND = Brand(name="Product name", accent="#c2410c", url="example.com")
VOICE = narrator("bf_emma")
MUSIC = "pad"                       # soft synthesised bed ducked under the voice
BASE_URL = "http://localhost:3000"  # the site the screen demo records (or pass --url)
URL_TEXT = "example.com"            # shown in the browser frame

FILM = [
    manim("Title", chapter="What it is"),
    screen("Demo", chapter="How to use it"),
    manim("Outro", chapter="Try it"),
]

YOUTUBE = """# YouTube upload details

**Title**
{title}: what it does and how to use it

**Description**
One or two sentences about the product.

In this video:
{chapters}

**Upload settings**
- Captions: upload captions.srt under Subtitles.
"""
