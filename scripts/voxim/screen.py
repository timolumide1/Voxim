"""Screen segments: record a website or web app in a browser, narrated, framed in a browser window.

A project lists its steps as ScreenScene(id, say, label, act). Each step holds until its
spoken line is finished. The recording is 1600x900 (pixel for pixel in the frame window), and
`frame()` places it in a browser window on a branded background.

Director actions: go(path), click(sel, navigates=False), type(sel, text), hover(sel),
scroll(px), zoom(sel, scale), unzoom(), label(text).
"""
from __future__ import annotations

import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import ff

VW, VH, DPR = 1600, 900, 1.0
LEAD = 0.25  # seconds of picture before each line starts

# Overlays live on <html>, outside <body>, so zooming the page doesn't zoom them.
OVERLAY_JS = """
(() => {
  if (window.__wt) return; window.__wt = true;
  const A = '__ACCENT__', INK = '__INK__';
  const css = document.createElement('style');
  css.textContent = `
    #wt-lab{position:fixed;left:28px;bottom:28px;z-index:2147483647;display:flex;align-items:center;gap:12px;
      padding:12px 20px 12px 14px;border-radius:14px;background:rgba(255,255,255,.96);color:${INK};
      font:700 19px/1.2 Inter,system-ui,sans-serif;box-shadow:0 10px 30px rgba(11,22,40,.16);
      transform:translateY(16px);opacity:0;transition:opacity .45s,transform .45s;pointer-events:none}
    #wt-lab i{width:6px;height:26px;border-radius:3px;background:${A};display:block}
    #wt-cur{position:fixed;z-index:2147483647;width:24px;height:24px;margin:-3px 0 0 -3px;pointer-events:none;
      transition:left .7s cubic-bezier(.3,.7,.2,1),top .7s cubic-bezier(.3,.7,.2,1)}
    .wt-ring{position:fixed;z-index:2147483646;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;
      border:3px solid ${A};pointer-events:none;animation:wtr .6s ease-out forwards}
    @keyframes wtr{to{transform:scale(3.4);opacity:0}}
    body{transition:transform 1.1s cubic-bezier(.45,.05,.2,1)}`;
  document.head.appendChild(css);
  const root = document.documentElement;
  const lab = document.createElement('div'); lab.id = 'wt-lab'; lab.innerHTML = '<i></i><span></span>'; root.appendChild(lab);
  const cur = document.createElement('div'); cur.id = 'wt-cur';
  cur.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24"><path d="M3 2l7 19 2.6-7.4L20 11z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  let p = {x: 640, y: 420}; try { p = JSON.parse(sessionStorage.getItem('wtpos')) || p; } catch {}
  cur.style.left = p.x + 'px'; cur.style.top = p.y + 'px'; root.appendChild(cur);
  window.__wtLabel = (t) => { lab.querySelector('span').textContent = t;
    lab.style.opacity = t ? 1 : 0; lab.style.transform = t ? 'none' : 'translateY(16px)'; };
  window.__wtMove = (x, y) => { cur.style.left = x + 'px'; cur.style.top = y + 'px';
    try { sessionStorage.setItem('wtpos', JSON.stringify({x, y})); } catch {} };
  window.__wtRing = (x, y) => { const r = document.createElement('div'); r.className = 'wt-ring';
    r.style.left = x + 'px'; r.style.top = y + 'px'; root.appendChild(r); setTimeout(() => r.remove(), 700); };
  window.__wtZoom = (x, y, s) => { const b = document.body;
    b.style.transformOrigin = x + 'px ' + (y + window.scrollY) + 'px'; b.style.transform = s === 1 ? '' : 'scale(' + s + ')'; };
})();
"""


class Director:
    def __init__(self, page, base: str, accent: str, ink: str):
        self.page, self.base = page, base.rstrip("/")
        self.js = OVERLAY_JS.replace("__ACCENT__", accent).replace("__INK__", ink)
        self._label = ""

    def _ready(self):
        # Never wait for "networkidle": pages that keep a connection open stall it for ~30s.
        self.page.wait_for_load_state("load")
        time.sleep(0.35)
        self.page.evaluate(self.js)
        self.page.evaluate("t => window.__wtLabel(t)", self._label)

    def go(self, path: str):
        self.page.goto(self.base + path)
        self._ready()

    def label(self, text: str):
        self._label = text
        self.page.evaluate(self.js)
        self.page.evaluate("t => window.__wtLabel(t)", text)

    def _point(self, selector: str):
        el = self.page.locator(selector).first
        el.scroll_into_view_if_needed()
        box = el.bounding_box()
        return el, box["x"] + min(box["width"] / 2, 60), box["y"] + box["height"] / 2

    def hover(self, selector: str):
        el, x, y = self._point(selector)
        self.page.evaluate("([x,y]) => window.__wtMove(x,y)", [x, y])
        self.page.mouse.move(x, y, steps=14)
        time.sleep(0.75)
        return el, x, y

    def click(self, selector: str, navigates: bool = False):
        el, x, y = self.hover(selector)
        self.page.evaluate("([x,y]) => window.__wtRing(x,y)", [x, y])
        time.sleep(0.25)
        el.click()
        if navigates:
            self._ready()
        time.sleep(0.35)

    def type(self, selector: str, text: str, delay_ms: int = 90):
        self.click(selector)
        loc = self.page.locator(selector).first
        loc.fill("")
        loc.press_sequentially(text, delay=delay_ms)
        time.sleep(0.35)

    def scroll(self, pixels: int, duration: float = 1.4):
        steps = 32
        for _ in range(steps):
            self.page.mouse.wheel(0, pixels / steps)
            time.sleep(duration / steps)
        time.sleep(0.3)

    def zoom(self, selector: str, scale: float = 1.35, hold: float = 0.0):
        """Smoothly magnify the page around an element (overlays stay put)."""
        el = self.page.locator(selector).first
        el.scroll_into_view_if_needed()
        b = el.bounding_box()
        self.page.evaluate("([x,y,s]) => window.__wtZoom(x,y,s)", [b["x"] + b["width"] / 2, b["y"] + b["height"] / 2, scale])
        time.sleep(1.15 + hold)

    def unzoom(self):
        self.page.evaluate("() => window.__wtZoom(0,0,1)")
        time.sleep(1.15)


@dataclass
class ScreenScene:
    id: str
    say: str
    label: str
    act: Callable[[Director], None]
    min_hold: float = 2.0


def record(scenes: list[ScreenScene], url: str, out: Path, durations: dict[str, float],
           accent: str, ink: str) -> list[dict]:
    """Record all scenes in one take. Returns cues [{id, start, end, say}] (seconds into `out`)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise SystemExit("Screen segments need Playwright: run `voxim setup --screen`.") from e
    tmp = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": VW, "height": VH}, device_scale_factor=DPR,
                                  record_video_dir=str(tmp),
                                  record_video_size={"width": int(VW * DPR), "height": int(VH * DPR)})
        page = ctx.new_page()
        rec0 = time.time()
        d = Director(page, url, accent, ink)
        d.go("/")  # warm-up; trimmed off below
        time.sleep(0.4)
        t0 = time.time()
        cues = []
        for sc in scenes:
            start = time.time() - t0
            d.label(sc.label)
            sc.act(d)
            need = max(durations.get(sc.id, len(sc.say.split()) / 2.5) + LEAD + 0.35, sc.min_hold)
            left = start + need - (time.time() - t0)
            if left > 0:
                time.sleep(left)
            cues.append({"id": sc.id, "start": round(start, 3), "end": round(time.time() - t0, 3), "say": sc.say})
        time.sleep(0.6)
        video = Path(page.video.path())
        ctx.close()
        browser.close()
    ff.run(["-ss", f"{t0 - rec0:.3f}", "-i", video, "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])
    return cues


def make_frame_assets(folder: Path, bg: str, soft: str, line: str, url_text: str) -> tuple[Path, Path]:
    """Background (1920x1080) and a browser-window overlay with a transparent content hole."""
    from PIL import Image, ImageDraw, ImageFilter

    W, H = 1920, 1080
    cw, ch, bar = 1600, 900, 46
    x0, y0 = (W - cw) // 2, (H - ch - bar) // 2
    hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    base = Image.new("RGB", (W, H), hexrgb(bg))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([-300, -380, 900, 520], fill=hexrgb(soft) + (255,))
    g.ellipse([1200, 560, 2300, 1500], fill=hexrgb(soft) + (200,))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    base.paste(glow, (0, 0), glow)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([x0, y0 + 22, x0 + cw, y0 + bar + ch + 22], 22, fill=(11, 22, 40, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    base.paste(shadow, (0, 0), shadow)
    bgp = folder / "frame_bg.png"
    base.save(bgp)

    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    d.rounded_rectangle([x0, y0, x0 + cw - 1, y0 + bar + ch - 1], 18, fill=(255, 255, 255, 255), outline=hexrgb(line) + (255,), width=2)
    d.rectangle([x0, y0 + bar, x0 + cw - 1, y0 + bar + ch - 1], fill=(0, 0, 0, 0))
    # keep rounded bottom corners: repaint the corner pixels outside the radius with background
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([x0, y0, x0 + cw - 1, y0 + bar + ch - 1], 18, fill=255)
    corners = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cm = Image.eval(mask, lambda v: 255 - v)
    box = Image.new("L", (W, H), 0)
    ImageDraw.Draw(box).rectangle([x0, y0 + bar + ch - 30, x0 + cw - 1, y0 + bar + ch - 1], fill=255)
    from PIL import ImageChops
    cm = ImageChops.multiply(cm, box)
    corners.paste(base.convert("RGBA"), (0, 0), cm)
    over = Image.alpha_composite(over, corners)
    d = ImageDraw.Draw(over)
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        cx = x0 + 26 + i * 22
        d.ellipse([cx - 7, y0 + bar // 2 - 7, cx + 7, y0 + bar // 2 + 7], fill=hexrgb(c) + (255,))
    pill = [x0 + cw // 2 - 260, y0 + 9, x0 + cw // 2 + 260, y0 + bar - 9]
    d.rounded_rectangle(pill, 14, fill=hexrgb("#f3eee9") + (255,))
    from PIL import ImageFont
    try:
        font = ImageFont.truetype(str(Path(__file__).parent / "fonts" / "Inter-Medium.ttf"), 17)
    except Exception:
        font = ImageFont.load_default()
    tw = d.textlength(url_text, font=font)
    d.text((x0 + cw // 2 - tw / 2, y0 + bar // 2 - 11), url_text, fill=hexrgb("#4a5568") + (255,), font=font)
    d.line([x0, y0 + bar - 1, x0 + cw - 1, y0 + bar - 1], fill=hexrgb(line) + (255,), width=2)
    ovp = folder / "frame_over.png"
    over.save(ovp)
    return bgp, ovp


def frame(clip: Path, out: Path, bgp: Path, ovp: Path, audio: Path | None = None):
    """Composite the recording into the browser window on the background."""
    cw, ch, bar = 1600, 900, 46
    x0, y0 = (1920 - cw) // 2, (1080 - ch - bar) // 2
    cmd = ["-loop", "1", "-i", str(bgp), "-i", str(clip), "-loop", "1", "-i", str(ovp)]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += ["-filter_complex",
            f"[1:v]scale={cw}:{ch}:flags=lanczos[c];[0:v][c]overlay={x0}:{y0 + bar}:shortest=1[v1];[v1][2:v]overlay=0:0:shortest=1,fps=30,format=yuv420p[v]",
            "-map", "[v]"]
    if audio:
        cmd += ["-map", "3:a", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-shortest", str(out)]
    ff.run(cmd)
