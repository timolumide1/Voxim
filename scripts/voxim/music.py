"""A soft, royalty-free ambient bed, synthesised (no downloads). Swap in any track with --music."""
from __future__ import annotations

import numpy as np

SR = 48000
# I–V–vi–IV in D major, voiced warm and low (Hz)
CHORDS = [
    [146.83, 220.00, 293.66, 369.99],   # D
    [110.00, 220.00, 277.18, 329.63],   # A
    [123.47, 246.94, 293.66, 369.99],   # Bm
    [98.00, 196.00, 293.66, 392.00],    # G
]


def pad(seconds: float, bar: float = 6.0, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float64)
    nb = int(np.ceil(seconds / bar)) + 1
    for k in range(nb):
        s = int(k * bar * SR)
        e = min(n, int((k + 1) * bar * SR + 2.5 * SR))  # overlap for smooth changes
        if s >= n:
            break
        tt = t[s:e] - t[s]
        env = np.minimum(1, tt / 2.0) * np.minimum(1, np.maximum(0, (tt[-1] - tt) / 2.5))
        for i, f in enumerate(CHORDS[k % 4]):
            det = 1 + rng.uniform(-0.002, 0.002)
            ph = rng.uniform(0, 2 * np.pi)
            v = (np.sin(2 * np.pi * f * det * tt + ph) + 0.35 * np.sin(2 * np.pi * 2 * f * tt + ph)
                 + 0.12 * np.sin(2 * np.pi * 3 * f * tt))
            v *= 1 + 0.15 * np.sin(2 * np.pi * 0.11 * tt + i)
            out[s:e] += v * env * (0.55 if i == 0 else 0.32)
    # gentle low-pass (one-pole) and stereo widening
    a = np.exp(-2 * np.pi * 1400 / SR)
    try:
        from scipy.signal import lfilter
        y = lfilter([1 - a], [1, -a], out)
    except ImportError:  # plain fallback
        y = np.empty_like(out); acc = 0.0
        for i in range(n):
            acc = (1 - a) * out[i] + a * acc; y[i] = acc
    fade = np.minimum(1, np.minimum(t / 3.0, (seconds - t) / 4.0))
    y *= np.clip(fade, 0, 1)
    y /= np.max(np.abs(y)) + 1e-9
    left = y
    right = np.roll(y, int(0.012 * SR))
    return (np.stack([left, right], axis=1) * 0.5).astype(np.float32)
