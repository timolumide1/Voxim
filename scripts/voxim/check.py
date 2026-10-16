"""Check a finished film: a contact sheet of each segment's middle and last frame, silent gaps, loudness.

    voxim check path/to/project     → out/check.png and a short report
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from . import ff


def check(project: str | Path) -> dict:
    out = Path(project).resolve() / "out"
    film, tl = out / "film.mp4", out / "timeline.json"
    if not film.exists():
        raise SystemExit(f"No {film}. Run: voxim build {project}")
    segs = json.loads(tl.read_text())
    tmp = out / ".check"; tmp.mkdir(exist_ok=True)
    for f in tmp.glob("*.png"):
        f.unlink()
    shots = []
    for s in segs:
        shots.append((f"{s['name']} middle", s["start"] + s["dur"] * 0.5))
        shots.append((f"{s['name']} end", s["start"] + s["dur"] - 0.8))
    for i, (label, t) in enumerate(shots):
        txt = label.replace(":", "\\:").replace("'", "")
        ff.run(["-ss", f"{max(t, 0):.2f}", "-i", film, "-frames:v", "1", "-vf",
                f"scale=640:-1,pad=iw:ih+34:0:34:color=0x222222,"
                f"drawtext=text='{txt}':x=10:y=7:fontsize=20:fontcolor=white:fontfile={(Path(__file__).parent / 'fonts' / 'Inter-Bold.ttf').as_posix()}",
                tmp / f"{i:03d}.png"])
    cols = 4
    rows = -(-len(shots) // cols)
    sheet = out / "check.png"
    ff.run(["-pattern_type", "glob", "-i", (tmp / "*.png").as_posix(), "-filter_complex",
            f"tile={cols}x{rows}:padding=6:color=white", "-frames:v", "1", sheet])

    log = subprocess.run([ff.ffmpeg(), "-nostdin", "-hide_banner", "-i", str(film), "-af",
                          "silencedetect=n=-45dB:d=1.5,ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    gaps = []
    for a, b in re.findall(r"silence_start: ([\d.]+).*?silence_end: ([\d.]+)", log, flags=re.S):
        gaps.append((float(a), float(b)))
    li = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
    report = {
        "length": round(ff.duration(film), 1),
        "segments": len(segs),
        "loudness_lufs": float(li[-1]) if li else None,
        "silent_gaps": [(round(a, 1), round(b, 1)) for a, b in gaps if b - a > 2.5],
        "sheet": str(sheet),
    }
    print(f"length {report['length']}s · {report['segments']} segments · loudness {report['loudness_lufs']} LUFS (aim −14 to −16)")
    if report["silent_gaps"]:
        print("silent gaps over 2.5 s (check these are intended pauses):",
              ", ".join(f"{a}–{b}s" for a, b in report["silent_gaps"]))
    else:
        print("no long silent gaps")
    print(f"contact sheet: {sheet}  (look at every frame: nothing cut off, overlapping or unreadable)")
    for f in tmp.glob("*.png"):
        f.unlink()
    tmp.rmdir()
    return report
