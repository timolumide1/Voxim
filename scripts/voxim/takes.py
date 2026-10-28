"""Your own voice: cut a recording of each clip into its narration lines.

    voxim takes DIR Intro=01.m4a PPE=02.m4a ...

For each scene named, reads its self.say(...) lines from scenes.py, finds the pauses in the
recording, recognises what was said in each stretch (Whisper, offline) and matches the
stretches to the lines in order. Each line is saved, cleaned up, to DIR/takes/<Scene>-<n>.wav,
and DIR/takes/takes.json maps each line's text to its file. Then in film.py:

    from voxim import recorded, narrator
    VOICE = recorded("takes", fallback=narrator("bf_emma"))

Lines with no take (a scene you haven't recorded yet) fall back to the synthetic narrator.
"""
from __future__ import annotations

import ast
import difflib
import json
import re
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

import numpy as np

from . import ff

ASR = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-base.en.tar.bz2"
RATE = 24000


def say_lines(scenes_py: Path, cls: str) -> list[str]:
    tree = ast.parse(scenes_py.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls:
            calls = sorted((n for n in ast.walk(node) if isinstance(n, ast.Call)
                            and getattr(n.func, "attr", "") == "say" and n.args), key=lambda n: (n.lineno, n.col_offset))
            try:
                return [ast.literal_eval(n.args[0]) for n in calls]
            except ValueError:
                raise SystemExit(f"{cls}: a say() line isn't plain text, so it can't be matched to a take")
    raise SystemExit(f"No scene class {cls} in {scenes_py}")


def plain(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[\[\]]", "", text)).strip()


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", plain(text).lower())


def _asr_dir() -> Path:
    from .voice import models_dir

    d = models_dir().parent / "whisper-base.en"
    if not (d / "base.en-encoder.int8.onnx").exists():
        print("downloading the speech recogniser (once, ~200 MB) …", flush=True)
        d.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as t:
            tar = Path(t) / "w.tar.bz2"
            urllib.request.urlretrieve(ASR, tar)
            with tarfile.open(tar) as tf:
                tf.extractall(t, filter="data")
            src = next(Path(t).glob("sherpa-onnx-whisper-base.en"))
            d.mkdir(exist_ok=True)
            for f in src.glob("base.en-*"):
                if "int8" in f.name or f.name.endswith("tokens.txt"):
                    f.rename(d / f.name)
    return d


def _recogniser():
    try:
        import sherpa_onnx as so
    except ImportError:
        raise SystemExit('voxim takes needs the speech recogniser: pip install "voxim[takes]"  (or: pip install sherpa-onnx)')

    d = _asr_dir()
    return so.OfflineRecognizer.from_whisper(encoder=str(d / "base.en-encoder.int8.onnx"),
                                             decoder=str(d / "base.en-decoder.int8.onnx"),
                                             tokens=str(d / "base.en-tokens.txt"), num_threads=2)


def load(path: Path, rate: int) -> np.ndarray:
    raw = subprocess.run([ff.ffmpeg(), "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def speech_runs(a: np.ndarray, rate: int, min_gap: float = 0.22) -> list[tuple[float, float]]:
    """Stretches of speech separated by pauses of at least min_gap seconds (threshold from the noise floor)."""
    hop = int(rate * 0.01)
    n = len(a) // hop
    db = 20 * np.log10(np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    floor, peak = np.percentile(db, 10), np.percentile(db, 95)
    on = db > max(floor + 12, peak - 30)
    runs, start, quiet = [], None, 0
    for i, v in enumerate(on):
        if v:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet * 0.01 >= min_gap:
                runs.append((start * 0.01, (i - quiet + 1) * 0.01)); start, quiet = None, 0
    if start is not None:
        runs.append((start * 0.01, (n - quiet) * 0.01))
    return [(s, e) for s, e in runs if e - s > 0.12]


def match(texts: list[str], lines: list[str]) -> list[tuple[int, int]]:
    """Split the stretches (in order) into len(lines) consecutive groups, best text match overall."""
    n, k = len(texts), len(lines)
    if n < k:
        raise ValueError(f"heard {n} stretches of speech for {k} lines")
    want = [norm(x) for x in lines]
    sim = lambda i, j, l: difflib.SequenceMatcher(None, norm(" ".join(texts[i:j])), want[l]).ratio()  # noqa: E731
    best = {(0, 0): (0.0, None)}
    for l in range(k):
        for j in range(l + 1, n - (k - l - 1) + 1):
            cands = [(best[(i, l)][0] + sim(i, j, l), i) for i in range(l, j) if (i, l) in best]
            if cands:
                best[(j, l + 1)] = max(cands)
    if (n, k) not in best:
        raise ValueError("couldn't line the recording up with the script")
    cuts, j = [], n
    for l in range(k, 0, -1):
        i = best[(j, l)][1]
        cuts.append((i, j)); j = i
    return cuts[::-1]


def clean(path_in: Path, path_out: Path, start: float, end: float):
    subprocess.run([ff.ffmpeg(), "-v", "error", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(path_in),
                    "-af", "highpass=f=80,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,"
                           "loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=in:d=0.03,areverse,afade=t=in:d=0.08,areverse",
                    "-ac", "1", "-ar", str(RATE), str(path_out)], check=True)


def takes(project: str | Path, pairs: list[str]):
    proj = Path(project).resolve()
    out = proj / "takes"
    out.mkdir(exist_ok=True)
    index_f = out / "takes.json"
    index = json.loads(index_f.read_text()) if index_f.exists() else {}
    rec = _recogniser()
    for pair in pairs:
        cls, _, file = pair.partition("=")
        src = Path(file).expanduser().resolve()
        lines = say_lines(proj / "scenes.py", cls)
        a = load(src, 16000)
        runs = speech_runs(a, 16000)
        heard = []
        for s, e in runs:
            st = rec.create_stream(); st.accept_waveform(16000, a[int(s * 16000): int(e * 16000)]); rec.decode_stream(st)
            heard.append(st.result.text.strip())
        try:
            groups = match(heard, lines)
        except ValueError as err:
            raise SystemExit(f"{cls}: {err}. Leave a clear pause (about a second) between lines and record it again.")
        print(f"{cls}  ({src.name}, {len(a) / 16000:.0f}s)")
        for n, ((i, j), line) in enumerate(zip(groups, lines), 1):
            s, e = runs[i][0], runs[j - 1][1]
            dst = out / f"{cls}-{n}.wav"
            clean(src, dst, max(0.0, s - 0.06), e + 0.18)
            got = " ".join(heard[i:j])
            score = difflib.SequenceMatcher(None, norm(got), norm(line)).ratio()
            flag = "" if score > 0.6 else "   <- check this one"
            print(f"  {n}. {e - s:4.1f}s  heard: {got[:90]}{flag}")
            index[plain(line)] = dst.name
    index_f.write_text(json.dumps(index, indent=1, ensure_ascii=False))
    print(f"wrote {index_f} ({len(index)} lines)")
