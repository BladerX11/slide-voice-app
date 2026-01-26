# Slide Voice App - Agent Guide

Slide Voice App is a desktop tool that edits PowerPoint slide notes, generates TTS audio, and embeds the audio back into `.pptx` files.

- Package manager: `uv`

Common commands

```bash
# Run (dev)
uv run scripts/run.py

# Build (dist/)
uv run scripts/build.py

# Manual compile Qt resources and QML module artifacts
# Default build/run scripts do this automatically
uv run scripts/utils.py

# Tests
uv run pytest

# Lint / format
uv run ruff check --select I --fix .
uv run ruff format .

# Typecheck
uv run ty check .
```

More detail

- docs/agents/commands.md
- docs/agents/project-structure.md
- docs/agents/python-style.md
- docs/agents/pyside-qml.md
- docs/agents/documentation.md
