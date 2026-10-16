"""Phases of the Moon: one scene per clip (see plan.md). Each narrates itself with self.say.

Look at one:  python -m manimgx inspect scenes.py TwoViews
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np  # noqa: E402
import manimgx as m  # noqa: E402

from voxim import Kit, Scene  # noqa: E402
from film import BRAND, VOICE  # noqa: E402

K = Kit(BRAND)
PI, TAU = np.pi, 2 * np.pi
LIT, DARK, EDGE = "#f3efe2", "#2b3446", "#4b5568"
SUN, EARTH, NIGHT = "#f5c542", "#3b82f6", "#1b2a4a"
PHASES = ["New moon", "Waxing crescent", "First quarter", "Waxing gibbous",
          "Full moon", "Waning gibbous", "Third quarter", "Waning crescent"]


# ── drawing helpers for this lesson ──────────────────────────────────────────────────────
def phase_disc(theta: float, r: float = 1.0):
    """The Moon as seen from Earth (Northern Hemisphere). theta: 0 new, π/2 first quarter, π full, 3π/2 third quarter."""
    th = theta % TAU
    base = m.Circle(radius=r, fill_color=DARK, fill_opacity=1, stroke_color=EDGE, stroke_width=2)
    if th < 1e-3 or TAU - th < 1e-3:
        return m.VGroup(base)
    side = 1 if th <= PI else -1          # waxing: lit on the right
    k = np.cos(th)
    ts = np.linspace(PI / 2, -PI / 2, 72)
    limb = [[side * r * np.cos(t), r * np.sin(t), 0] for t in ts]
    term = [[side * k * r * np.cos(t), r * np.sin(t), 0] for t in ts[::-1]]
    lit = m.Polygon(*(limb + term), fill_color=LIT, fill_opacity=1, stroke_width=0)
    return m.VGroup(base, lit)


def lit_ball(center, r: float, toward: float = PI, lit=LIT, dark=DARK):
    """A ball lit on the half facing direction `toward` (radians; π = light from the left)."""
    c = np.array(center, dtype=float)
    base = m.Circle(radius=r, fill_color=dark, fill_opacity=1, stroke_color=EDGE, stroke_width=1.5).move_to(c)
    ts = np.linspace(toward - PI / 2, toward + PI / 2, 48)
    half = m.Polygon(*[c + r * np.array([np.cos(t), np.sin(t), 0]) for t in ts], fill_color=lit, fill_opacity=1, stroke_width=0)
    return m.VGroup(base, half)


def earth(center, r: float = 0.5):
    return lit_ball(center, r, PI, lit=EARTH, dark=NIGHT)


def sun_rays(x0: float, x1: float, ys, label: bool = True):
    rays = m.VGroup(*[m.Arrow([x0, y, 0], [x1, y, 0], buff=0, color=SUN, stroke_width=4,
                              max_tip_length_to_length_ratio=0.12) for y in ys])
    if not label:
        return rays
    lab = K.body("Sunlight", size=22, color=SUN, weight="BOLD").next_to(rays, m.UP, buff=0.15).align_to(rays, m.LEFT)
    return m.VGroup(rays, lab)


def sun(center, r: float = 1.0):
    glow = m.VGroup(*[m.Circle(radius=r * (1 + 0.25 * i), fill_color=SUN, fill_opacity=0.12, stroke_width=0) for i in range(3, 0, -1)])
    core = m.Circle(radius=r, fill_color=SUN, fill_opacity=1, stroke_width=0)
    return m.VGroup(glow, core).move_to(center)


def phase_name(theta: float) -> str:
    return PHASES[int(round((theta % TAU) / (PI / 4))) % 8]


class Base(Scene):
    voice = VOICE


# ── clips ───────────────────────────────────────────────────────────────────────────────
class MirrorLight(Base):
    def construct(self):
        h = K.top_heading("Moonlight", "Does the Moon make its own light?")
        s = sun([-4.9, -1.2, 0], 1.1)
        mp, ep = np.array([1.2, 0.9, 0]), np.array([4.9, -1.6, 0])
        moon_dark = m.Circle(radius=0.55, fill_color=DARK, fill_opacity=1, stroke_color=EDGE, stroke_width=2).move_to(mp)
        d = s.get_center() - mp
        moon_lit = lit_ball(mp, 0.55, np.arctan2(d[1], d[0]))
        e = earth(ep, 0.75)
        e_lab = K.body("Earth", size=24, color=BRAND.ink).next_to(e, m.DOWN, buff=0.2)
        m_lab = K.body("Moon", size=24, color=BRAND.ink).next_to(moon_dark, m.UP, buff=0.2)
        u = (mp - s.get_center()) / np.linalg.norm(mp - s.get_center())
        ray_in = m.Arrow(s.get_center() + u * 1.25, mp - u * 0.68, buff=0, color=SUN, stroke_width=6)
        ray_out = m.Arrow(mp, ep, buff=0.8, color="#fff3c4", stroke_width=6)
        eye = K.callout(e, "Your eyes", direction=m.LEFT, buff=0.7, size=24)
        foot = K.footer("Not to scale")

        self.add(h)
        self.say("[Does the Moon make its own light?]",
                 m.AnimationGroup(m.FadeIn(e), m.FadeIn(e_lab), m.FadeIn(moon_dark), m.FadeIn(m_lab)))
        self.say("[No.] On its own, the Moon would be dark. It's more like a mirror.", m.Indicate(moon_dark, color=EDGE))
        self.say("[Light from the Sun] travels across space to the Moon, [bounces off its surface], "
                 "[and reaches your eyes] here on Earth.",
                 m.AnimationGroup(m.FadeIn(s, scale=0.8), m.GrowArrow(ray_in), m.FadeIn(foot)),
                 m.FadeIn(moon_lit, run_time=0.8),
                 m.AnimationGroup(m.GrowArrow(ray_out), m.FadeIn(eye)))
        self.say("So moonlight is really [sunlight, reflected].",
                 m.Circumscribe(moon_lit, color=SUN, shape=m.Circle, buff=0.15))
        self.wait(0.6)


class HalfLit(Base):
    def construct(self):
        h = K.top_heading("Half is always lit", "Sunlight comes from one side")
        rays = sun_rays(-6.8, -2.6, np.linspace(-1.6, 1.0, 5))
        c = np.array([0.6, -0.45, 0])
        big = lit_ball(c, 1.65)
        day = K.body("Day side", size=26, color=BRAND.ink, weight="BOLD").move_to(c + [-0.85, -2.1, 0])
        night = K.body("Night side", size=26, color=BRAND.muted, weight="BOLD").move_to(c + [0.95, -2.1, 0])
        split = m.DashedLine(c + [0, 1.85, 0], c + [0, -1.85, 0], color=BRAND.muted, stroke_width=2)

        self.add(h)
        self.say("[Sunlight] always comes from one direction.",
                 m.AnimationGroup(m.FadeIn(big[0]), m.LaggedStart(*[m.GrowArrow(a) for a in rays[0]], lag_ratio=0.1),
                                  m.FadeIn(rays[1])))
        self.say("So [the half of the Moon that faces the Sun] is lit, and [the other half] is dark. "
                 "That's the Moon's night side.",
                 m.AnimationGroup(m.FadeIn(big[1]), m.FadeIn(day)),
                 m.AnimationGroup(m.Create(split), m.FadeIn(night)))

        # the orbit: the lit half keeps facing the Sun
        ec, R = np.array([0.8, -0.4, 0]), 2.4
        a = m.ValueTracker(PI * 0.75)
        orbit = m.DashedVMobject(m.Circle(radius=R, stroke_color=EDGE, stroke_width=2).move_to(ec), num_dashes=60)
        e = earth(ec, 0.45)
        start = lit_ball(ec + R * np.array([np.cos(PI * 0.75), np.sin(PI * 0.75), 0]), 0.36)
        moon = m.always_redraw(lambda: lit_ball(ec + R * np.array([np.cos(a.get_value()), np.sin(a.get_value()), 0]), 0.36))
        new_h = K.top_heading("Half is always lit", "Wherever the Moon is in its orbit")
        self.say("Now [let the Moon travel around Earth].",
                 m.AnimationGroup(m.FadeOut(m.VGroup(day, night, split)), m.Transform(big, start),
                                  m.FadeIn(e), m.Create(orbit), m.Transform(h, new_h), run_time=1.6))
        self.remove(big); self.add(moon)
        self.say("[Wherever it goes, the lit half still faces the Sun.]",
                 a.animate(run_time=6, rate_func=m.linear).set_value(PI * 0.75 + TAU))
        self.say("[Half the Moon is always lit.] What changes is how much of that lit half we can see from Earth.",
                 m.Circumscribe(moon, color=SUN, shape=m.Circle, buff=0.12))
        self.wait(0.6)


class TwoViews(Base):
    def construct(self):
        th = m.ValueTracker(0.0)
        ec, R = np.array([-3.3, -0.05, 0]), 2.05
        rays = sun_rays(-7.0, -5.85, [-0.9, -0.35, 0.2], label=False)
        rlab = K.body("Sunlight", size=20, color=SUN, weight="BOLD").next_to(rays, m.UP, buff=0.15).align_to(rays, m.LEFT)
        orbit = m.DashedVMobject(m.Circle(radius=R, stroke_color=EDGE, stroke_width=2).move_to(ec), num_dashes=60)
        e = earth(ec, 0.42)
        pos = lambda: ec + R * np.array([np.cos(PI + th.get_value()), np.sin(PI + th.get_value()), 0])
        moon = m.always_redraw(lambda: lit_ball(pos(), 0.3))
        sight = m.always_redraw(lambda: m.DashedLine(ec, pos(), buff=0.45, color=BRAND.accent2, stroke_width=3))
        left_k = K.kicker("Seen from far above", size=22).move_to([-3.3, 2.75, 0])
        top = m.VGroup(left_k, rays, rlab, orbit, e, sight, moon)

        divider = m.Line([0.35, 2.9, 0], [0.35, -2.8, 0], color=BRAND.line, stroke_width=2)
        rc = np.array([3.55, 0.35, 0])
        right_k = K.kicker("What we see from Earth", size=22).move_to([3.55, 2.75, 0])
        disc = m.always_redraw(lambda: phase_disc(th.get_value(), 1.45).move_to(rc))
        name = m.always_redraw(lambda: K.head(phase_name(th.get_value()), size=40).move_to(rc + [0, -2.05, 0]))

        def day_text():
            d = th.get_value() / TAU * 29.5
            return K.body("Day 29.5" if d > 29.45 else f"Day {d:.0f}", size=26, color=BRAND.muted).move_to(rc + [0, -2.75, 0])
        day = m.always_redraw(day_text)
        right = m.VGroup(right_k, disc, name, day)

        self.say("Here's the Moon's orbit, [seen from far above Earth]. And here's [what we see from Earth].",
                 m.FadeIn(top), m.AnimationGroup(m.Create(divider), m.FadeIn(right)))
        self.say("[At new moon], the Moon is between Earth and the Sun. Its lit half faces away from us, "
                 "so we see almost nothing.", m.Circumscribe(moon, color=SUN, shape=m.Circle, buff=0.12))
        self.say("As the Moon moves along its orbit, [we start to see a thin slice of the lit half]: a waxing crescent.",
                 th.animate(run_time=3).set_value(PI / 4))
        self.say("[About a week in], we see half the disc lit. That's the first quarter.",
                 th.animate(run_time=2.5).set_value(PI / 2))
        self.say("[At full moon], Earth is between the Sun and the Moon, and we see the whole lit half.",
                 th.animate(run_time=4).set_value(PI))
        self.say("[Then the lit part shrinks], through waning gibbous, third quarter and waning crescent, "
                 "[back to new moon].",
                 th.animate(run_time=4).set_value(3 * PI / 2), th.animate(run_time=3).set_value(TAU))
        self.say("[One full trip] takes about twenty-nine and a half days.", m.Indicate(day, color=BRAND.accent))
        self.wait(0.6)


class Shadow(Base):
    def construct(self):
        wg, strike, rg = K.misconception(
            "Earth's shadow covers part of the Moon, and that makes the phases.",
            "The dark part is the Moon's own night side. Earth's shadow only reaches the Moon during a lunar eclipse.")
        self.say("Many people think [Earth's shadow] makes the phases. [It doesn't.]",
                 m.FadeIn(wg, shift=m.UP * 0.2), m.Create(strike))
        self.say("[The dark part we see is the Moon's own night side.]", m.FadeIn(rg, shift=m.UP * 0.2))
        self.wait(0.4)
        self.clear_all()

        h = K.top_heading("Earth's shadow", "Where it really points")
        ec, R, er = np.array([-0.9, -0.15, 0]), 2.05, 0.45
        rays = sun_rays(-6.8, -3.4, [-1.2, -0.3, 0.6])
        shadow = m.Polygon(ec + [0, er, 0], ec + [6.9, er * 0.55, 0], ec + [6.9, -er * 0.55, 0], ec + [0, -er, 0],
                           fill_color="#000000", fill_opacity=0.55, stroke_width=0)
        s_lab = K.body("Earth's shadow", size=22, color=BRAND.muted, weight="BOLD").move_to(ec + [5.0, 0.75, 0])
        orbit = m.DashedVMobject(m.Circle(radius=R, stroke_color=EDGE, stroke_width=2).move_to(ec), num_dashes=60)
        e = earth(ec, er)
        a = m.ValueTracker(-PI / 2)              # first quarter: below Earth in this view
        dim = m.ValueTracker(0.0)

        def moon_now():
            p = ec + R * np.array([np.cos(a.get_value()), np.sin(a.get_value()), 0])
            lit = m.interpolate_color(m.ManimColor(LIT), m.ManimColor("#9a4a2e"), dim.get_value())
            return lit_ball(p, 0.32, lit=lit)
        moon = m.always_redraw(moon_now)
        inset = phase_disc(PI / 2, 0.5).move_to([3.0, -1.75, 0])
        in_lab = K.body("From Earth:\nhalf looks dark", size=22, color=BRAND.ink).next_to(inset, m.RIGHT, buff=0.3)
        ecl = K.body("Lunar eclipse", size=26, color="#e07a5f", weight="BOLD").move_to(ec + [R + 1.35, -0.75, 0])
        foot = K.footer("Not to scale")

        self.play(m.FadeIn(h), m.FadeIn(rays), m.FadeIn(e), m.Create(orbit), m.FadeIn(foot), run_time=0.8)
        self.say("Earth's shadow points [straight away from the Sun]. At first quarter, [the Moon is nowhere near it], "
                 "[yet half of what we see is dark].",
                 m.AnimationGroup(m.FadeIn(shadow), m.FadeIn(s_lab)), m.FadeIn(moon),
                 m.AnimationGroup(m.FadeIn(inset), m.FadeIn(in_lab)))
        self.say("[Only at some full moons], when the Sun, Earth and Moon line up exactly, the Moon passes "
                 "through Earth's shadow. [That's a lunar eclipse], and it's rare.",
                 m.AnimationGroup(m.FadeOut(m.VGroup(inset, in_lab)), a.animate(run_time=2.5).set_value(0)),
                 m.AnimationGroup(dim.animate.set_value(1), m.FadeIn(ecl)))
        self.wait(0.6)


class Sequence(Base):
    def construct(self):
        h = K.top_heading("The lunar cycle", "The eight phases, in order")
        xs = np.linspace(-5.6, 5.6, 8)
        cells = []
        for i, (x, n) in enumerate(zip(xs, PHASES)):
            d = phase_disc(i * PI / 4, 0.6).move_to([x, 0.45, 0])
            lab = K.body(n.replace(" ", "\n"), size=22, color=BRAND.ink).next_to(d, m.DOWN, buff=0.25)
            cells.append(m.VGroup(d, lab))
        y = -1.75
        wax = m.Arrow([xs[0] - 0.5, y, 0], [xs[4] - 0.05, y, 0], buff=0, color=BRAND.accent, stroke_width=5)
        wan = m.Arrow([xs[4] + 0.05, y, 0], [xs[7] + 0.6, y, 0], buff=0, color=BRAND.accent2, stroke_width=5)
        wax_l = K.body("Waxing: the lit part grows", size=24, color=BRAND.accent, weight="BOLD").next_to(wax, m.DOWN, buff=0.18)
        wan_l = K.body("Waning: it shrinks", size=24, color=BRAND.accent2, weight="BOLD").next_to(wan, m.DOWN, buff=0.18)
        days = K.head("about 29.5 days", size=34, color=BRAND.accent).to_corner(m.UR, buff=0.8).shift(m.DOWN * 0.35)

        self.add(h)
        self.say("Here are the eight phases in order: [new moon, waxing crescent, first quarter, waxing gibbous, "
                 "full moon, waning gibbous, third quarter, waning crescent].",
                 m.LaggedStart(*[m.FadeIn(c, shift=m.UP * 0.2) for c in cells], lag_ratio=0.5))
        self.say("From new to full, the lit part grows. [We call that waxing.] "
                 "After full moon it shrinks. [That's waning.]",
                 m.AnimationGroup(m.GrowArrow(wax), m.FadeIn(wax_l)),
                 m.AnimationGroup(m.GrowArrow(wan), m.FadeIn(wan_l)))
        self.say("[Then it's new moon again.] [The whole cycle] takes about twenty-nine and a half days.",
                 m.Indicate(cells[0], color=BRAND.accent, scale_factor=1.15), m.FadeIn(days, shift=m.DOWN * 0.2))
        self.wait(0.8)


class Check(Base):
    def construct(self):
        card, timer = K.question("Tonight is a first quarter moon. What will it look like in about a week?", seconds=6)
        self.say("[Tonight is a first quarter moon.] What will it look like in about a week? "
                 "Pause the video and decide.", m.FadeIn(card, shift=m.UP * 0.3))
        self.play(timer)
        self.clear_all()

        q = phase_disc(PI / 2, 0.9).move_to([-4.9, 0.3, 0])
        f = phase_disc(PI, 0.9).move_to([-0.5, 0.3, 0])
        arr = m.Arrow(q.get_right(), f.get_left(), buff=0.25, color=BRAND.accent, stroke_width=5)
        arr_l = K.body("about 7 days", size=24, color=BRAND.accent, weight="BOLD").next_to(arr, m.UP, buff=0.15)
        ql = K.body("First quarter", size=26, color=BRAND.ink).next_to(q, m.DOWN, buff=0.3)
        fl = K.body("Full moon", size=26, color=BRAND.ink, weight="BOLD").next_to(f, m.DOWN, buff=0.3)
        ans = m.VGroup(K.kicker("Answer"), K.head("Full moon", size=56),
                       K.para("A week is about a quarter of the cycle, so the Moon goes a quarter of the way round.",
                              width=24, size=26)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25).move_to([4.3, 0.3, 0])
        self.say("[It'll be a full moon.] A week is about a quarter of the cycle, so the Moon moves "
                 "[from first quarter to full].",
                 m.AnimationGroup(m.FadeIn(ans, shift=m.LEFT * 0.2), m.FadeIn(q), m.FadeIn(ql)),
                 m.AnimationGroup(m.GrowArrow(arr), m.FadeIn(arr_l), m.FadeIn(f), m.FadeIn(fl)))
        self.wait(0.8)
