# Voxim

*Vox* (voice) + *anim*ation. A Claude skill that makes narrated, captioned explainer videos with
animated diagrams.

Give Claude a lesson plan or teaching notes and it works out which parts of the lesson a visual
would actually help, a process, a cycle, something spatial or invisible, a misconception. It
animates those parts and hands back:

- one short clip per concept, with captions burned in, ready to drop into slides or an LMS
- the whole set joined as one film, plus captions (`.srt`)
- a teacher's guide saying where each clip fits in the lesson

It also makes product explainers with a recorded, narrated website demo and YouTube details.

Everything runs on your own machine: animation by [ManimGX](https://pypi.org/project/manimgx/),
narration by [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) (offline, no API key), assembly by
ffmpeg. You only install the skill; its first run installs the rest.

## Install the skill

- **Claude Code:**
  ```bash
  git clone https://github.com/timolumide1/Voxim ~/.claude/skills/voxim
  ```
- **Claude (web or desktop app):** download this repository as a ZIP (green **Code** button →
  **Download ZIP**), then Settings → Capabilities → Skills → upload it.

Then ask for what you need, for example: *"Here's my lesson plan on photosynthesis for Year 8.
Make short animated clips for the parts that need a visual."*

The first run installs a private Python 3.13 environment in `~/.voxim/` and downloads the
voice model (about 340 MB). This needs a machine where Claude can run commands (Claude Code, or
Claude with code execution and network access).

## Use it by hand

```bash
bash scripts/install.sh                     # once (Windows: scripts/install.ps1)
X=~/.voxim/venv/bin/voxim
$X new lesson my-lesson                     # a working starter project
$X build my-lesson                          # → my-lesson/out/
$X check my-lesson                          # contact sheet + audio report
```

## What's inside

```
SKILL.md                     what Claude follows
references/lesson-mode.md    the visual audit, narration and design rules for lessons
references/scene-cookbook.md tested patterns: steps, cycles, labelled diagrams, equations, graphs, 3D…
references/product-mode.md   product explainers with a recorded website demo
references/troubleshooting.md
scripts/                     the `voxim` Python package, installers, fonts, templates
examples/moon-phases/        a full worked lesson: teacher's notes → plan → scenes → clips
examples/cookbook/           every cookbook pattern as a runnable scene
```

## Licence

MIT for this skill's code. Bundled fonts (Inter, Plus Jakarta Sans) are under the SIL Open Font
Licence. ManimGX and Kokoro are installed from their own sources under their own licences.
