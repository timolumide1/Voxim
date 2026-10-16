# Troubleshooting

**"No matching distribution found for manimgx"**: ManimGX needs Python 3.13 or newer. The
installer makes its own 3.13 environment with `uv`; use `~/.voxim/venv/bin/voxim`, not
a system Python.

**The voice model won't download** (blocked network): download `kokoro-v1.0.onnx` and
`voices-v1.0.bin` from https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
on another machine, put them in a folder, and set `KOKORO_MODELS=/that/folder`.

**"No space left on device"**: video intermediates are large. Delete `<project>/build/*.norm.mov`,
`build/*.mp4` and `out/` from projects you're done with; they are rebuilt when needed. If space
doesn't come back after deleting, a stopped-but-alive ffmpeg is still holding a deleted file:
`pkill -9 ffmpeg`. Then check with `df -h`.

**A build seems stuck**: rendering takes 5–30 s per scene, the join and caption burn-in a minute or
two for a few minutes of video. Run long builds in the background and watch the log. Each finished
segment is kept, so a stopped build resumes where it left off.

**Captions aren't burned in**: the ffmpeg in use has no libass. Install a full ffmpeg (Homebrew,
apt or winget) and rebuild; the `.srt` files are written either way.

**Text overlaps or runs off the frame**: `python -m manimgx inspect scenes.py Scene` lists every
overlap and off-frame object with its line number. Fix layout before building. A line through text
that you put there on purpose (a strike-through) is reported too; that one is fine.

**Something sits under the captions**: burned captions cover the strip below y = −2.6. Move content
up, and watch moving objects (orbits, falling things) at their lowest point.

**Axis numbers are invisible**: ManimGX's default axis numbers are white. Use `K.axes(...)`.

**The voice mispronounces a word**: spell it the way it's said in the `say` text ("H two O",
"Kuh-NEE-dee"), and map it back for captions with `CAPTION_TEXT` in film.py.

**A scene re-renders every time / never re-renders**: segments re-render when their class, the
shared code in scenes.py, the brand, the voice or the kit change. Force one with `--only Name`, or
all with `--force`.
