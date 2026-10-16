"""voxim: make narrated explainer and lesson videos.

  voxim setup [--screen]        download the voice model, check ffmpeg (and Playwright for screen demos)
  voxim new lesson|product DIR  start a project from a template
  voxim build DIR [--only A,B]  render what changed and assemble out/film.mp4 (+ clips, guide)
  voxim check DIR               contact sheet + audio report for out/film.mp4
  voxim voices                  list narrator voices
  voxim say "text" [--voice V]  hear a voice: writes say.wav
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATES = Path(__file__).parent / "templates"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="voxim", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("setup"); p.add_argument("--screen", action="store_true", help="also install a browser for screen demos")
    p = sub.add_parser("new"); p.add_argument("kind", choices=["lesson", "product"]); p.add_argument("dir")
    p = sub.add_parser("build"); p.add_argument("dir")
    p.add_argument("--only", help="comma list of segment names to re-make (default: whatever changed)")
    p.add_argument("--force", action="store_true", help="re-make every segment")
    p.add_argument("--url", help="base URL for screen segments")
    p.add_argument("--music", help="'pad', 'none' or an audio file (overrides film.py)")
    p.add_argument("--no-clips", action="store_true")
    p = sub.add_parser("check"); p.add_argument("dir")
    sub.add_parser("voices")
    p = sub.add_parser("say"); p.add_argument("text"); p.add_argument("--voice", default="af_heart"); p.add_argument("--speed", type=float, default=1.0)
    a = ap.parse_args(argv)

    if a.cmd == "setup":
        from . import ff
        from .voice import ensure_models, speak

        print("ffmpeg:", ff.ffmpeg())
        print("voice model:", ensure_models())
        samples, rate = speak("Ready.")
        print(f"narrator works ({len(samples) / rate:.1f}s test line)")
        import manimgx  # noqa: F401
        print("ManimGX:", getattr(manimgx, "__version__", "installed"))
        if a.screen:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=False)
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("Setup complete.")
    elif a.cmd == "new":
        dst = Path(a.dir)
        if dst.exists() and any(dst.iterdir()):
            raise SystemExit(f"{dst} is not empty")
        shutil.copytree(TEMPLATES / a.kind, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        print(f"Started a {a.kind} project in {dst}. Edit film.py and scenes.py, then: voxim build {dst}")
    elif a.cmd == "build":
        from .build import build

        build(a.dir, only=a.only.split(",") if a.only else None, url=a.url, music=a.music, force=a.force, no_clips=a.no_clips)
    elif a.cmd == "check":
        from .check import check

        check(a.dir)
    elif a.cmd == "voices":
        from .voice import voices

        print(" ".join(voices()))
    elif a.cmd == "say":
        import soundfile as sf

        from .voice import speak

        samples, rate = speak(a.text, voice=a.voice, speed=a.speed)
        sf.write("say.wav", samples, rate)
        print("wrote say.wav")


if __name__ == "__main__":
    main()
