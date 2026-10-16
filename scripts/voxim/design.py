"""One look for every scene: a Brand (colours, fonts, logo) and a Kit of drawing helpers.

    from voxim import Brand, Kit
    BRAND = Brand(name="Moon Phases", accent="#2563eb")
    K = Kit(BRAND)
    K.title_card("Why does the Moon change shape?", "Grade 7 · Earth & Space")

The frame is 14.2 units wide and 8 tall, centred on the origin. Keep content inside x ±6.4 and
y from −2.6 to +3.4: burned-in captions cover the strip below y = −2.6.
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import manimgx as m

FONTS = str(Path(__file__).parent / "fonts")


@dataclass
class Brand:
    name: str = ""
    bg: str = "#fcfaf8"          # page background
    ink: str = "#0b1628"         # main text
    muted: str = "#4a5568"       # secondary text
    accent: str = "#c2410c"      # highlights, key numbers
    accent2: str = "#1e6fd9"     # a second series, actions
    soft: str = "#ffeee3"        # tinted panels
    line: str = "#ede4dc"        # rules, axes, borders
    good: str = "#1f7a4d"
    bad: str = "#b42318"
    head_font: str = "Plus Jakarta Sans"
    body_font: str = "Inter"
    font_dir: str | None = FONTS  # folder holding the .ttf files for the fonts above
    logo_svg: str | None = None
    url: str = ""

    @classmethod
    def dark(cls, **kw) -> "Brand":
        """A dark preset (chalkboard feel); override any colour with keywords."""
        base = dict(bg="#10151f", ink="#f4f1ea", muted="#b9c0cc", accent="#f59e0b", accent2="#60a5fa",
                    soft="#1d2533", line="#2c3647", good="#4ade80", bad="#f87171")
        return cls(**{**base, **kw})


@dataclass
class Kit:
    b: Brand
    fonts: list = field(default_factory=list)

    def __post_init__(self):
        self.fonts = [self.b.font_dir] if self.b.font_dir else []
        m.config.background_color = self.b.bg

    # ── text ─────────────────────────────────────────────────────────────────────────
    def head(self, s: str, size: float = 64, color: str | None = None, weight: str = "BOLD", **kw):
        return m.Text(s, font=self.b.head_font, weight=weight, font_size=size,
                      color=color or self.b.ink, font_paths=self.fonts, **kw)

    def body(self, s: str, size: float = 30, color: str | None = None, weight: str = "NORMAL", **kw):
        return m.Text(s, font=self.b.body_font, weight=weight, font_size=size,
                      color=color or self.b.muted, font_paths=self.fonts, **kw)

    def para(self, s: str, width: int = 42, size: float = 30, color: str | None = None, **kw):
        """Body text wrapped to `width` characters a line."""
        return self.body("\n".join(textwrap.wrap(s, width)), size=size, color=color, **kw)

    def kicker(self, s: str, size: float = 22, color: str | None = None):
        """Small uppercase label above a heading."""
        return m.Text(s.upper(), font=self.b.body_font, weight="BOLD", font_size=size,
                      color=color or self.b.accent, font_paths=self.fonts)

    def num(self, value: float, size: float = 96, color: str | None = None, prefix: str = "", suffix: str = "", decimals: int = 0):
        return self.head(f"{prefix}{value:,.{decimals}f}{suffix}", size=size, color=color or self.b.accent, weight="ULTRABOLD")

    def math(self, tex: str, size: float = 48, color: str | None = None):
        """An equation (LaTeX syntax; no LaTeX install needed)."""
        return m.MathTex(tex, font_size=size, color=color or self.b.ink)

    # ── pieces ───────────────────────────────────────────────────────────────────────
    def logo(self, height: float = 1.2):
        if self.b.logo_svg and Path(self.b.logo_svg).exists():
            return m.SVGMobject(self.b.logo_svg, height=height)
        return m.RoundedRectangle(corner_radius=0.25, width=height, height=height,
                                  fill_color=self.b.accent, fill_opacity=1, stroke_width=0)

    def panel(self, w: float, h: float, color: str | None = None, radius: float = 0.25):
        return m.RoundedRectangle(corner_radius=radius, width=w, height=h,
                                  fill_color=color or ("#ffffff" if self._light else self.b.soft), fill_opacity=1,
                                  stroke_color=self.b.line, stroke_width=2)

    @property
    def _light(self) -> bool:
        h = self.b.bg.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return (0.299 * r + 0.587 * g + 0.114 * b) > 140

    def heading_block(self, kicker: str, title: str, size: float = 54):
        k, t = self.kicker(kicker), self.head(title, size=size)
        return m.VGroup(k, t).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.22)

    def top_heading(self, kicker: str, title: str, size: float = 50):
        """A heading block placed top-left, the usual spot for a scene's title."""
        return self.heading_block(kicker, title, size).to_corner(m.UL, buff=0.75)

    def underline(self, mob, color: str | None = None):
        """A soft highlighter stroke under a word."""
        r = m.Rectangle(width=mob.width * 1.04, height=mob.height * 0.32,
                        fill_color=color or self.b.soft, fill_opacity=1, stroke_width=0)
        return r.move_to(mob.get_bottom() + m.UP * mob.height * 0.18).set_z_index(-1)

    def title_card(self, title: str, subtitle: str = "", kicker: str = ""):
        """Opening card: optional kicker, big title, subtitle, all centred."""
        parts = ([self.kicker(kicker, size=26)] if kicker else []) + [self.head(title, size=72, weight="ULTRABOLD")]
        if subtitle:
            parts.append(self.body(subtitle, size=34))
        g = m.VGroup(*parts).arrange(m.DOWN, buff=0.4)
        if g.width > 12.6:
            g.scale_to_fit_width(12.6)
        return g

    def section(self, number: str, title: str, subtitle: str = ""):
        """Full-screen chapter card."""
        n = self.head(number, size=40, color=self.b.accent)
        bar = m.Rectangle(width=0.9, height=0.08, fill_color=self.b.accent, fill_opacity=1, stroke_width=0)
        t = self.head(title, size=76)
        parts = [n, bar, t] + ([self.body(subtitle, size=32)] if subtitle else [])
        return m.VGroup(*parts).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3).to_edge(m.LEFT, buff=1.3)

    def footer(self, text: str):
        return self.body(text, size=18, color=self.b.muted).to_corner(m.DR, buff=0.35)

    # ── teaching pieces ──────────────────────────────────────────────────────────────
    def callout(self, target, text: str, direction=m.UP, buff: float = 0.9, size: float = 30, color: str | None = None):
        """A label with an arrow pointing at `target`. Returns VGroup(label, arrow)."""
        c = color or self.b.accent
        lab = self.body(text, size=size, color=self.b.ink, weight="BOLD")
        lab.next_to(target, direction, buff=buff)
        arrow = m.Arrow(lab.get_edge_center(-direction), target.get_edge_center(direction), buff=0.08,
                        color=c, stroke_width=5, max_tip_length_to_length_ratio=0.3)
        return m.VGroup(lab, arrow)

    def steps(self, items: list[str], size: float = 34, width: int = 44, buff: float = 0.42):
        """Numbered steps of a process. Returns (group, rows); reveal rows one by one."""
        rows = m.VGroup()
        for i, s in enumerate(items, 1):
            dot = m.Circle(radius=0.33, fill_color=self.b.accent, fill_opacity=1, stroke_width=0)
            n = self.head(str(i), size=26, color="#ffffff").move_to(dot)
            t = self.para(s, width=width, size=size, color=self.b.ink)
            rows.add(m.VGroup(m.VGroup(dot, n), t).arrange(m.RIGHT, buff=0.35, aligned_edge=m.UP))
        rows.arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)
        return rows, list(rows)

    def cycle(self, items: list[str], radius: float = 2.6, size: float = 30, node_w: float = 3.2):
        """A loop of stages joined by curved arrows (water cycle, cell cycle, a feedback loop).

        Returns (group, nodes, arrows). Nodes sit on a wide oval, clockwise from the top."""
        import numpy as np

        n = len(items)
        nodes, arrows = [], []
        pts = [radius * np.array([1.4 * np.cos(np.pi / 2 - 2 * np.pi * i / n), 0.92 * np.sin(np.pi / 2 - 2 * np.pi * i / n), 0])
               for i in range(n)]
        for s, p in zip(items, pts):
            t = self.para(s, width=16, size=size, color=self.b.ink, weight="BOLD")
            box = self.panel(max(node_w, t.width + 0.5), t.height + 0.45, radius=0.2)
            nodes.append(m.VGroup(box, t.move_to(box)).move_to(p))
        for i in range(n):
            a, b = nodes[i], nodes[(i + 1) % n]
            arc = m.CurvedArrow(self._edge_toward(a, b), self._edge_toward(b, a), angle=-0.5,
                                color=self.b.accent, stroke_width=5)
            arrows.append(arc)
        return m.VGroup(*arrows, *nodes), nodes, arrows

    @staticmethod
    def _edge_toward(a, b):
        import numpy as np

        d = b.get_center() - a.get_center()
        d = d / (np.linalg.norm(d) + 1e-9)
        return a.get_center() + np.array([d[0] * a.width / 2, d[1] * a.height / 2, 0]) * 1.1

    def timeline(self, events: list[tuple[str, str]], width: float = 12.0, size: float = 26):
        """Dates on a line, labels alternating above and below. Returns (group, line, marks)."""
        line = m.Line(m.LEFT * width / 2, m.RIGHT * width / 2, color=self.b.muted, stroke_width=4)
        marks = []
        n = len(events)
        for i, (when, what) in enumerate(events):
            x = -width / 2 + width * (i + 0.5) / n
            dot = m.Dot([x, 0, 0], radius=0.11, color=self.b.accent)
            w = self.head(when, size=size + 6, color=self.b.accent)
            t = self.para(what, width=16, size=size, color=self.b.ink)
            lab = m.VGroup(w, t).arrange(m.DOWN, buff=0.12)
            up = i % 2 == 0
            lab.next_to(dot, m.UP if up else m.DOWN, buff=0.35)
            marks.append(m.VGroup(dot, lab))
        return m.VGroup(line, *marks), line, marks

    def compare(self, left_title: str, left: list[str], right_title: str, right: list[str],
                left_color: str | None = None, right_color: str | None = None, size: float = 26):
        """Two panels side by side. Returns (group, left_panel, right_panel)."""
        def col(title, items, c):
            h = self.head(title, size=34, color=c)
            rows = m.VGroup(*[self.para("•  " + s, width=26, size=size, color=self.b.ink) for s in items])
            rows.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25)
            inner = m.VGroup(h, rows).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.4)
            box = self.panel(5.9, max(inner.height + 0.9, 3.5))
            inner.move_to(box).align_to(box, m.LEFT).shift(m.RIGHT * 0.45)
            return m.VGroup(box, inner)
        lp = col(left_title, left, left_color or self.b.accent)
        rp = col(right_title, right, right_color or self.b.accent2)
        g = m.VGroup(lp, rp).arrange(m.RIGHT, buff=0.5, aligned_edge=m.UP)
        return g, lp, rp

    def definition(self, term: str, meaning: str, kicker: str = "Key word"):
        """A key-word card: kicker, the term, its meaning."""
        k = self.kicker(kicker)
        t = self.head(term, size=60, color=self.b.accent)
        d = self.para(meaning, width=44, size=32, color=self.b.ink)
        inner = m.VGroup(k, t, d).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3)
        box = self.panel(inner.width + 1.2, inner.height + 1.0)
        return m.VGroup(box, inner.move_to(box))

    def question(self, text: str, seconds: float = 5.0, kicker: str = "Pause and think"):
        """A check-for-understanding card with a shrinking timer bar.

        Returns (card, timer_animation): show the card, then self.play(timer_animation)."""
        k = self.kicker(kicker, size=24)
        q = self.para(text, width=36, size=42, color=self.b.ink, weight="BOLD")
        inner = m.VGroup(k, q).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.35)
        box = self.panel(max(inner.width + 1.4, 9), inner.height + 1.6)
        inner.move_to(box).shift(m.UP * 0.2)
        bar = m.Rectangle(width=box.width - 1.0, height=0.12, fill_color=self.b.accent, fill_opacity=1, stroke_width=0)
        bar.next_to(inner, m.DOWN, buff=0.45).align_to(inner, m.LEFT)
        card = m.VGroup(box, inner, bar)
        timer = bar.animate(run_time=seconds, rate_func=m.linear).stretch_to_fit_width(0.01, about_edge=m.LEFT)
        return card, timer

    def misconception(self, wrong: str, right: str, size: float = 34):
        """A common wrong idea, crossed out, then the right one.

        Returns (wrong_group, strike, right_group): show wrong, Create(strike), then show right."""
        wk = self.kicker("Common idea", color=self.b.bad)
        # one Text per line so each line gets its own strike-through
        wt = m.VGroup(*[self.body(line, size=size, color=self.b.muted) for line in textwrap.wrap(wrong, 40)])
        wt.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.18)
        wg = m.VGroup(wk, wt).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.2)
        rk = self.kicker("What really happens", color=self.b.good)
        rt = self.para(right, width=40, size=size, color=self.b.ink, weight="BOLD")
        rg = m.VGroup(rk, rt).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.2)
        m.VGroup(wg, rg).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.8).move_to(m.ORIGIN)
        strike = m.VGroup(*[m.Line(t.get_left() + m.LEFT * 0.1, t.get_right() + m.RIGHT * 0.1,
                                   color=self.b.bad, stroke_width=5).shift(m.UP * t.height * 0.08) for t in wt])
        return wg, strike, rg

    def summary(self, title: str, points: list[str], size: float = 32):
        """End-of-lesson recap: a heading and ticked points. Returns (group, rows)."""
        h = self.head(title, size=54)
        rows = m.VGroup()
        for p in points:
            tick = self.head("✓", size=size + 6, color=self.b.good)
            rows.add(m.VGroup(tick, self.para(p, width=48, size=size, color=self.b.ink)).arrange(m.RIGHT, buff=0.3, aligned_edge=m.UP))
        rows.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.35)
        g = m.VGroup(h, rows).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.6).move_to(m.ORIGIN)
        return g, list(rows)

    # ── numbers and charts ───────────────────────────────────────────────────────────
    def axes(self, x_range, y_range, x_length: float = 9, y_length: float = 5, x_label: str = "", y_label: str = "",
             decimals: int = 0, size: float = 26):
        """Axes in the brand's colours with readable numbers. Returns (axes, labels); plot with axes.plot(f)."""
        ax = m.Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length, tips=False,
                    axis_config={"color": self.b.muted, "include_numbers": True, "font_size": size, "stroke_width": 3,
                                 "decimal_number_config": {"color": self.b.ink, "num_decimal_places": decimals}})
        labels = m.VGroup()
        if x_label:
            labels.add(self.body(x_label, size=size, color=self.b.ink).next_to(ax.x_axis, m.DOWN, buff=0.55))
        if y_label:
            labels.add(self.body(y_label, size=size, color=self.b.ink).rotate(1.5708).next_to(ax.y_axis, m.LEFT, buff=0.7))
        return ax, labels

    def count_up(self, start: float, end: float, size: float = 96, color: str | None = None,
                 prefix: str = "", suffix: str = "", decimals: int = 0):
        """A number that counts: returns (mobject, tracker). Animate tracker.animate.set_value(end)."""
        tr = m.ValueTracker(start)
        mob = m.always_redraw(lambda: self.num(tr.get_value(), size=size, color=color, prefix=prefix,
                                               suffix=suffix, decimals=decimals))
        return mob, tr

    def hbars(self, items: list[tuple[str, float]], width: float = 7.5, row: float = 0.62,
              color: str | None = None, label_w: float = 3.6, fmt=lambda v: f"{v:,.0f}", highlight: int | None = None):
        """Horizontal bar chart. Returns (group, bars, values); grow with grow_bars()."""
        top = max(v for _, v in items)
        rows, bars, vals = m.VGroup(), [], []
        for i, (name, v) in enumerate(items):
            c = (self.b.accent if highlight is None or i == highlight else self.b.line) if color is None else color
            lab = self.body(name, size=26, color=self.b.ink)
            lab.move_to(m.ORIGIN, aligned_edge=m.RIGHT).shift(m.LEFT * 0.25)
            track = m.Rectangle(width=width, height=row * 0.62, fill_color=self.b.line, fill_opacity=0.55, stroke_width=0)
            track.move_to(m.ORIGIN, aligned_edge=m.LEFT)
            bar = m.Rectangle(width=max(width * v / top, 0.02), height=row * 0.62, fill_color=c, fill_opacity=1, stroke_width=0)
            bar.move_to(m.ORIGIN, aligned_edge=m.LEFT)
            val = self.body(fmt(v), size=24, color=self.b.ink, weight="BOLD").next_to(bar, m.RIGHT, buff=0.15)
            g = m.VGroup(lab, track, bar, val).shift(m.DOWN * i * row)
            rows.add(g); bars.append(bar); vals.append(val)
        rows.move_to(m.ORIGIN).shift(m.RIGHT * label_w / 2 * 0.6)
        return rows, bars, vals

    def grow_bars(self, bars, vals, lag: float = 0.12):
        return m.LaggedStart(*[m.AnimationGroup(m.GrowFromEdge(b, m.LEFT), m.FadeIn(v, shift=m.RIGHT * 0.2))
                               for b, v in zip(bars, vals)], lag_ratio=lag)


class Scene(m.Scene):
    """A scene with a narrator and a clear() helper. Set `voice` on a subclass or in film.py."""

    def clear_all(self, t: float = 0.5):
        if self.mobjects:
            self.play(*[m.FadeOut(x) for x in self.mobjects], run_time=t)
