"""The recorded demo. Each step holds until its line is spoken.

Director actions: d.go(path), d.click(selector, navigates=False), d.type(selector, text),
d.hover(selector), d.scroll(px), d.zoom(selector, scale), d.unzoom()
"""
from voxim.screen import ScreenScene

SCREENS = [
    ScreenScene("home", "This is the home page.", "Home", lambda d: d.go("/")),
    ScreenScene("scroll", "Scroll down to see what it offers.", "Features", lambda d: d.scroll(600)),
]
# A film with several screen segments can name each list after its segment, e.g. Demo = [...]
