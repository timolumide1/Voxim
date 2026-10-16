"""ffmpeg helpers. Uses the system ffmpeg when there is one, otherwise the static build from imageio-ffmpeg."""
from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:  # pragma: no cover
        raise SystemExit("ffmpeg not found. Install it (brew install ffmpeg / apt install ffmpeg / winget install ffmpeg) "
                         "or `pip install imageio-ffmpeg`.") from e


def run(args: list, **kw):
    """Run ffmpeg with `args` (without the leading 'ffmpeg')."""
    return subprocess.run([ffmpeg(), "-nostdin", "-y", "-hide_banner", "-loglevel", "error", *map(str, args)], check=True, **kw)


def probe(p: Path) -> str:
    return subprocess.run([ffmpeg(), "-hide_banner", "-i", str(p)], capture_output=True, text=True).stderr


def duration(p: Path) -> float:
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe(p))
    if not m:
        raise RuntimeError(f"can't read duration of {p}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def has_audio(p: Path) -> bool:
    return "Audio:" in probe(p)


def has_filter(name: str) -> bool:
    out = subprocess.run([ffmpeg(), "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return any(line.split()[1:2] == [name] for line in out.splitlines() if line.strip())
