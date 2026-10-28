"""Build a narrated film from a project folder.

    voxim build path/to/project            # re-renders only what changed
    voxim build path/to/project --only Intro,Orbit

A project folder holds:
  film.py     settings: TITLE, MODE, BRAND, VOICE, FILM (running order), and optional extras
  scenes.py   ManimGX scenes, one class per animated segment (each narrates itself with self.say)
  screens.py  SCREENS: steps for a recorded website demo (only if FILM has screen segments)

Everything it makes goes in <project>/out/ (intermediates in <project>/build/):
  film.mp4, captions.srt, timeline.json, clips/NN-Name.mp4 (+ .srt),
  guide.md (lesson mode) or youtube.md (product mode)
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from . import ff, Seg, __version__
from . import music as music_mod

T = 0.5        # crossfade between segments
TAIL = 0.6     # hold added to each segment's end so a fade never clips the voice
FPS = 30
FONTS = Path(__file__).parent / "fonts"


# ── small helpers ──────────────────────────────────────────────────────────────────────
def ts(t: float) -> str:
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m_, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m_:02}:{s:02},{ms:03}"


def clock(t: float) -> str:
    mm, ss = divmod(int(round(t)), 60)
    return f"{mm}:{ss:02d}"


def parse_srt(p: Path) -> list[tuple[float, float, str]]:
    if not p.exists():
        return []
    out = []
    for block in re.split(r"\n\s*\n", p.read_text(encoding="utf-8").strip()):
        lines = block.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            a, b = [x.strip() for x in lines[1].split("-->")]
            f = lambda s: (lambda h, m, rest: int(h) * 3600 + int(m) * 60 + float(rest.replace(",", ".")))(*s.split(":"))
            out.append((f(a), f(b), " ".join(lines[2:])))
    return out


def write_srt(caps, path: Path, offset: float = 0.0):
    lines = []
    for n, (s_, e_, t) in enumerate(caps, 1):
        lines += [str(n), f"{ts(offset + s_)} --> {ts(offset + e_)}", t, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def chunks(text: str, max_chars: int = 80) -> list[str]:
    parts = re.split(r"(?<=[.?!:,])\s+", text)
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + 1 + len(p) > max_chars:
            out.append(cur); cur = p
        else:
            cur = f"{cur} {p}".strip()
    return out + ([cur] if cur else [])


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def scene_fingerprint(scenes_py: Path, settings: str, cls: str) -> str:
    """Changes when the class, the module-level code it relies on, the brand/voice or the kit change."""
    src = scenes_py.read_text(encoding="utf-8")
    tree = ast.parse(src)
    own, shared = "", []
    for node in tree.body:
        seg = ast.get_source_segment(src, node) or ""
        if isinstance(node, ast.ClassDef) and node.name == cls:
            own = seg
        elif isinstance(node, ast.ClassDef):
            # base classes other scenes inherit from count as shared
            if not any(isinstance(n, ast.FunctionDef) and n.name == "construct" for n in node.body):
                shared.append(seg)
        else:
            shared.append(seg)
    kit = (Path(__file__).parent / "design.py").read_bytes()
    h = hashlib.sha256()
    for part in [own, *shared, settings, __version__]:
        h.update(part.encode() if isinstance(part, str) else part)
    h.update(kit)
    return h.hexdigest()[:16]


def normalise(src: Path, dst: Path):
    """Same size, rate, pixel format and audio layout everywhere, plus a held tail."""
    cmd = ["-i", src]
    if not ff.has_audio(src):
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    a = "0:a" if ff.has_audio(src) else "1:a"
    length = ff.duration(src) + TAIL
    cmd += ["-filter_complex",
            f"[0:v]scale=1920:1080:flags=lanczos,fps={FPS},format=yuv420p,tpad=stop_mode=clone:stop_duration={TAIL + 6},settb=AVTB[v];"
            f"[{a}]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={length:.3f},atrim=0:{length:.3f}[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{length:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-c:a", "pcm_s16le", dst]
    ff.run(cmd)


CAPTION_STYLE = ("FontName=Inter,FontSize=16,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H1A141414,"
                 "BackColour=&H00000000,BorderStyle=3,Outline=5,Shadow=0,MarginV=24")


def finish(src: Path, dst: Path, music: str, music_db: float, srt: Path | None):
    """Mix the music bed (ducked under the voice), set loudness, optionally burn captions."""
    total = ff.duration(src)
    vf = []
    if srt is not None:
        if ff.has_filter("subtitles"):
            # paths in this filter are escaped awkwardly, so run from the caption's folder
            vf = ["-vf", f"subtitles={srt.name}:fontsdir={FONTS.as_posix()}:force_style='{CAPTION_STYLE}'"]
        else:
            print("  (this ffmpeg can't burn captions: no libass. Captions are in the .srt files.)")
    # always yuv420p / High profile: 4:4:4 H.264 won't play in QuickTime, Windows, phones or browsers
    vcodec = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high"]
    aout = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart"]
    cwd = str(srt.parent) if vf else None
    if music == "none":
        args = ["-i", src.resolve(), *vf, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", *vcodec, *aout, dst.resolve()]
    else:
        bed = Path(music) if music not in ("pad", "") else dst.parent / f".{dst.stem}.bed.wav"
        if music in ("pad", ""):
            sf.write(bed, music_mod.pad(total + 1), 48000)
        args = ["-i", src.resolve(), "-stream_loop", "-1", "-i", bed.resolve(), "-filter_complex",
                f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={music_db}dB[m];"
                "[0:a]asplit=2[vo][sc];"
                "[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=600[md];"
                "[vo][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                "-map", "0:v", "-map", "[a]", *vf, *vcodec, *aout, "-shortest", dst.resolve()]
    subprocess.run([ff.ffmpeg(), "-nostdin", "-y", "-hide_banner", "-loglevel", "error", *map(str, args)], check=True, cwd=cwd)
    if music in ("pad", ""):
        (dst.parent / f".{dst.stem}.bed.wav").unlink(missing_ok=True)


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


# ── the build ──────────────────────────────────────────────────────────────────────────
def build(project: str | Path, only: list[str] | None = None, url: str | None = None, music: str | None = None,
          force: bool = False, no_clips: bool = False):
    proj = Path(project).resolve()
    if not (proj / "film.py").exists():
        raise SystemExit(f"No film.py in {proj}. Start one with: voxim new lesson {proj}")
    sys.path.insert(0, str(proj))
    film = load_module("film", proj / "film.py")
    work, out = proj / "build", proj / "out"
    work.mkdir(exist_ok=True); out.mkdir(exist_ok=True)

    mode = getattr(film, "MODE", "lesson")
    B = film.BRAND
    voice = getattr(film, "VOICE", None)
    segs = [s if isinstance(s, Seg) else Seg(*s) for s in film.FILM]
    music = music or getattr(film, "MUSIC", "none" if mode == "lesson" else "pad")
    music_db = getattr(film, "MUSIC_DB", -17)
    burn = getattr(film, "BURN_CAPTIONS", mode == "lesson")
    cap_fn = getattr(film, "CAPTION_TEXT", lambda s: s)
    base_url = url or getattr(film, "BASE_URL", "http://localhost:3000")
    only = set(only or [])
    settings = repr(B) + repr(voice)
    unknown = only - {s.name for s in segs}
    if unknown:
        raise SystemExit(f"--only names not in FILM: {', '.join(sorted(unknown))}")

    built = []  # (seg, normalised video, captions)
    for s in segs:
        raw, norm, stamp = work / f"{s.name}.mp4", work / f"{s.name}.norm.mov", work / f"{s.name}.stamp"
        if s.kind == "manim":
            fp = scene_fingerprint(proj / "scenes.py", settings, s.name)
        else:
            fp = hashlib.sha256((proj / "screens.py").read_bytes() + settings.encode() + base_url.encode()).hexdigest()[:16]
        stale = not raw.exists() or not stamp.exists() or stamp.read_text() != fp
        want = force or (s.name in only if only else stale)
        if s.kind == "manim":
            if want:
                print(f"render  {s.name}", flush=True)
                subprocess.run([sys.executable, "-m", "manimgx", "render", str(proj / "scenes.py"), s.name,
                                "-r", "1920x1080", "--fps", str(FPS), "--crf", "16", "-o", str(raw)], cwd=proj, check=True)
            caps = parse_srt(raw.with_suffix(".srt"))
        elif s.kind == "screen":
            from .screen import LEAD, frame, make_frame_assets, record
            from .voice import speak

            mod = load_module("screens", proj / "screens.py")
            steps = getattr(mod, s.name, None) or mod.SCREENS
            caps_file = work / f"{s.name}.caps.json"
            if want or not caps_file.exists():
                print(f"record  {s.name}", flush=True)
                vdir = work / "voice"; vdir.mkdir(exist_ok=True)
                durs = {}
                for sc in steps:
                    kw = dict(voice=voice.voice, speed=voice.speed, lang=voice.lang) if voice else {}
                    samples, rate = speak(sc.say, **kw)
                    sf.write(vdir / f"{sc.id}.wav", samples, rate)
                    durs[sc.id] = len(samples) / rate
                clip = work / f"{s.name}.raw.mp4"
                cues = record(steps, base_url, clip, durs, B.accent, B.ink)
                length = ff.duration(clip)
                track = np.zeros(int((length + 1) * 48000), dtype=np.float32)
                caps = []
                for c in cues:
                    s_, r_ = sf.read(vdir / f"{c['id']}.wav", dtype="float32")
                    if r_ != 48000:
                        idx = np.linspace(0, len(s_) - 1, int(len(s_) * 48000 / r_))
                        s_ = np.interp(idx, np.arange(len(s_)), s_).astype(np.float32)
                    st = int((c["start"] + LEAD) * 48000)
                    track[st:st + len(s_)] += s_[: max(0, len(track) - st)]
                    begin, dur = c["start"] + LEAD, len(s_) / 48000
                    pieces = chunks(cap_fn(c["say"])); total = sum(len(p) for p in pieces); t = begin
                    for p in pieces:
                        d = dur * len(p) / total; caps.append((t, t + d, p)); t += d
                wav = work / f"{s.name}.voice.wav"
                sf.write(wav, track, 48000)
                bgp, ovp = make_frame_assets(work, B.bg, B.soft, B.line, getattr(film, "URL_TEXT", B.url or base_url))
                frame(clip, raw, bgp, ovp, wav)
                caps_file.write_text(json.dumps(caps))
                wav.unlink(missing_ok=True)
            caps = [tuple(x) for x in json.loads(caps_file.read_text())]
        else:
            raise SystemExit(f"unknown segment kind {s.kind!r} for {s.name}")
        if want or not norm.exists():
            normalise(raw, norm)
            stamp.write_text(fp)
        caps = [(a, b, cap_fn(t)) for a, b, t in caps]
        built.append((s, norm, caps))

    # ── join with crossfades ───────────────────────────────────────────────────────────
    durs = [ff.duration(p) for _, p, _ in built]
    offsets, acc = [], 0.0
    for i, d in enumerate(durs):
        offsets.append(acc - i * T if i else 0.0)
        acc += d
    joined = work / "joined.mov"
    if len(built) == 1:
        ff.run(["-i", built[0][1], "-c", "copy", joined])
    else:
        inputs = sum([["-i", p] for _, p, _ in built], [])
        fv, fa, graph = "[0:v]", "[0:a]", []
        for i in range(1, len(built)):
            graph.append(f"{fv}[{i}:v]xfade=transition=fade:duration={T}:offset={offsets[i]:.3f},format=yuv420p[v{i}]")
            graph.append(f"{fa}[{i}:a]acrossfade=d={T}:c1=tri:c2=tri[a{i}]")
            fv, fa = f"[v{i}]", f"[a{i}]"
        ff.run([*inputs, "-filter_complex", ";".join(graph), "-map", fv, "-map", fa,
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "pcm_s16le", joined])
    total = ff.duration(joined)

    all_caps = [(off + a, off + b, t) for (s, _, caps), off in zip(built, offsets) for a, b, t in caps]
    write_srt(all_caps, out / "captions.srt")
    print("finish  film.mp4", flush=True)
    finish(joined, out / "film.mp4", music, music_db, out / "captions.srt" if burn else None)
    joined.unlink(missing_ok=True)

    # ── one clip per segment (lesson mode, or any segment marked clip=True) ───────────────
    clip_rows = []
    if not no_clips and (mode == "lesson" or getattr(film, "CLIPS", False)):
        cdir = out / "clips"; cdir.mkdir(exist_ok=True)
        for i, ((s, norm, caps), d) in enumerate(zip(built, durs), 1):
            if not s.clip:
                continue
            name = f"{i:02d}-{slug(s.name)}"
            write_srt(caps, cdir / f"{name}.srt")
            dst = cdir / f"{name}.mp4"
            if want_clip(dst, norm):
                print(f"clip    {name}", flush=True)
                finish(norm, dst, music, music_db, cdir / f"{name}.srt" if burn else None)
            clip_rows.append((name, s, d))

    # ── timeline, chapters, guide ────────────────────────────────────────────────────────
    (out / "timeline.json").write_text(json.dumps(
        [{"name": s.name, "start": round(o, 2), "dur": round(d, 2), "chapter": s.chapter, "use": s.use}
         for (s, _, _), o, d in zip(built, offsets, durs)], indent=1))
    chapters = [(o, s.chapter) for (s, _, _), o in zip(built, offsets) if s.chapter]
    if chapters and chapters[0][0] > 0:
        chapters.insert(0, (0.0, "Introduction"))
    chap_txt = "\n".join(f"{'0:00' if o == 0 else clock(o + 0.25)} {c}" for o, c in chapters)
    title = getattr(film, "TITLE", B.name or proj.name)

    if mode == "lesson":
        lines = [f"# {title}: teacher's guide", ""]
        for key, label in (("AUDIENCE", "Class"), ("OBJECTIVES", "Learning objectives"), ("SOURCE", "Built from")):
            v = getattr(film, key, None)
            if v:
                lines += [f"**{label}:**" + (f" {v}" if isinstance(v, str) else "")]
                if not isinstance(v, str):
                    lines += [f"- {x}" for x in v]
                lines.append("")
        lines += [f"**Full video:** film.mp4 ({clock(total)}), captions in captions.srt", "",
                  "## Clips, in lesson order", "",
                  "| Clip | Length | Where it fits in the lesson | Starts in film.mp4 |",
                  "|---|---|---|---|"]
        off_by = {s.name: o for (s, _, _), o in zip(built, offsets)}
        for name, s, d in clip_rows:
            lines.append(f"| clips/{name}.mp4 | {clock(d)} | {s.use or s.chapter or '—'} | {clock(off_by[s.name])} |")
        notes = getattr(film, "NOTES", None)
        if notes:
            lines += ["", "## Notes", ""] + [f"- {n}" for n in notes]
        if chapters:
            lines += ["", "## Chapters (for YouTube or an LMS)", "", chap_txt]
        lines += ["", "Captions are burned into the videos." if burn else "Captions: upload the .srt beside each video.",
                  "Narration is a synthetic voice (Kokoro TTS). Animations made with ManimGX.", ""]
        (out / "guide.md").write_text("\n".join(lines), encoding="utf-8")
    yt = getattr(film, "YOUTUBE", None)
    if yt or mode != "lesson":
        yt = yt or "# YouTube upload details\n\n**Title**\n{title}\n\n**Description**\n\nIn this video:\n{chapters}\n"
        (out / "youtube.md").write_text(yt.format(chapters=chap_txt, title=title), encoding="utf-8")

    print(f"Done: {out / 'film.mp4'} ({clock(total)})" + (f", {len(clip_rows)} clips" if clip_rows else ""))
    return out


def want_clip(dst: Path, norm: Path) -> bool:
    return not dst.exists() or dst.stat().st_mtime < norm.stat().st_mtime
