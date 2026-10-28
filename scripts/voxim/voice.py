"""The narrator: Kokoro text-to-speech, offline, no API key.

    from voxim import narrator
    class MyScene(m.Scene):
        voice = narrator("af_heart", lang="en-us")

Voices (first letter = language, second = f/m):
  American English  af_heart af_bella af_nicole af_sarah am_michael am_adam am_eric
  British English   bf_emma bf_isabella bf_alice bm_george bm_daniel bm_lewis
  Spanish ef_dora em_alex · French ff_siwis · Hindi hf_alpha hm_omega · Italian if_sara im_nicola
  Portuguese (BR) pf_dora pm_alex · Japanese jf_alpha jm_kumo · Mandarin zf_xiaoxiao zm_yunxi
Run `voxim voices` for the full list.

The two model files (~340 MB) are downloaded once by `voxim setup` into
$KOKORO_MODELS (default ~/.voxim/kokoro).
"""
from __future__ import annotations

import os
import urllib.request
from functools import lru_cache
from pathlib import Path

import numpy as np

RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
LANG_OF = {"a": "en-us", "b": "en-gb", "e": "es", "f": "fr-fr", "h": "hi", "i": "it", "p": "pt-br", "j": "ja", "z": "cmn"}


def models_dir() -> Path:
    if os.environ.get("KOKORO_MODELS"):
        return Path(os.environ["KOKORO_MODELS"]).expanduser()
    legacy = Path.home() / "kokoro"
    if all((legacy / f).exists() for f in FILES):
        return legacy
    return Path(os.environ.get("VOXIM_HOME", Path.home() / ".voxim")).expanduser() / "kokoro"


def ensure_models(verbose: bool = True) -> Path:
    d = models_dir()
    d.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        p = d / f
        if p.exists() and p.stat().st_size > 1_000_000:
            continue
        if verbose:
            print(f"downloading {f} into {d} …", flush=True)
        tmp = p.with_suffix(p.suffix + ".part")
        urllib.request.urlretrieve(RELEASE + f, tmp)
        tmp.rename(p)
    return d


def _espeak_data() -> str | None:
    """espeak-ng can't read its data from a path longer than ~150 characters (deep home folders,
    long Windows user names). Copy it somewhere short when that happens."""
    import shutil
    import tempfile

    import espeakng_loader

    src = Path(espeakng_loader.get_data_path())
    if len(str(src)) < 120:
        return None
    home = Path(os.environ.get("VOXIM_HOME", Path.home() / ".voxim")).expanduser()
    for base in (home, Path(tempfile.gettempdir())):
        dst = base / "espeak-ng-data"
        if len(str(dst)) < 120:
            if not (dst / "phontab").exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            return str(dst)
    return None


@lru_cache(maxsize=1)
def _engine():
    from kokoro_onnx import Kokoro
    from kokoro_onnx.config import EspeakConfig

    d = ensure_models(verbose=True)
    data = _espeak_data()
    cfg = EspeakConfig(data_path=data) if data else None
    return Kokoro(str(d / FILES[0]), str(d / FILES[1]), espeak_config=cfg)


def voices() -> list[str]:
    return sorted(_engine().get_voices())


def speak(text: str, voice: str = "af_heart", speed: float = 1.0, lang: str | None = None) -> tuple[np.ndarray, int]:
    """Samples (float32, mono) and their rate for `text`."""
    lang = lang or LANG_OF.get(voice[:1], "en-us")
    audio, rate = _engine().create(text, voice=voice, speed=speed, lang=lang)
    return np.asarray(audio, dtype=np.float32), rate


class narrator:
    """A ManimGX voice: called with text, returns a Speech that ManimGX times word by word.

    ManimGX caches speech in voice/ beside the scene file, keyed by this repr and the text."""

    def __init__(self, voice: str = "af_heart", speed: float = 1.0, lang: str | None = None):
        self.voice, self.speed = voice, speed
        self.lang = lang or LANG_OF.get(voice[:1], "en-us")

    def __repr__(self) -> str:
        return f"kokoro({self.voice!r}, speed={self.speed}, lang={self.lang!r})"

    def __call__(self, text: str):
        import manimgx as m

        audio, rate = speak(text, self.voice, self.speed, self.lang)
        return m.Speech(audio[:, None], text=text, rate=rate)


class recorded:
    """Your own recorded narration, cut into lines by `voxim takes`; lines without a take use `fallback`.

        VOICE = recorded("takes", fallback=narrator("bf_emma"))
    """

    def __init__(self, folder: str = "takes", fallback=None):
        import hashlib
        import inspect
        import json

        here = Path(inspect.stack()[1].filename).resolve().parent
        self.folder = (here / folder) if not Path(folder).is_absolute() else Path(folder)
        f = self.folder / "takes.json"
        self.index = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        self.fallback = fallback or narrator("af_heart")
        h = hashlib.sha256()
        for name in sorted(set(self.index.values())):
            p = self.folder / name
            if p.exists():
                h.update(p.read_bytes())
        self._stamp = h.hexdigest()[:12]

    def __repr__(self) -> str:
        return f"recorded({self._stamp}, fallback={self.fallback!r})"

    def __call__(self, text: str):
        import re

        import manimgx as m

        key = re.sub(r"\s+", " ", re.sub(r"[\[\]]", "", text)).strip()
        name = self.index.get(key)
        if name and (self.folder / name).exists():
            return m.Speech(str(self.folder / name), text=text)
        return self.fallback(text)
