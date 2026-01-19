# Slide Voice App - Agent Instructions

This document provides guidelines, commands, and standards for AI agents and developers working on the `slide-voice-app`.
Follow these instructions strictly to maintain code quality, consistency, and stability.

## Project Overview

**Goal:**
A desktop application to load PowerPoint (`.pptx`) files, extract and edit slide notes, generate Text-to-Speech (TTS) audio using various providers, and embed the audio back into the presentation.

**Stack:**
- **Language:** Python 3.10+
- **UI Framework:** PySide6 (Qt Quick/QML)
- **Package Manager:** `uv`
- **Build Tool:** Nuitka (for distribution)

## Project Structure

```
slide-voice-app/
├── src/slide_voice_app/     # Main application source code
│   ├── __main__.py          # Application entry point
│   ├── ui/                  # QML files for UI
│   └── rc_resources.py      # Generated resource file (do not edit manually)
├── scripts/                 # Build and development scripts
│   ├── run.py               # Run application in development mode
│   ├── build.py             # Build application for distribution
│   └── utils.py             # Shared utilities for scripts
├── docs/                    # Documentation
│   ├── dev/                 # Developer documentation
│   └── user/                # User documentation
├── resources.qrc            # Qt resource collection file
└── pyproject.toml           # Project configuration
```

## Build, Run, and Test Commands

### Running the Application (Development)
```bash
uv run scripts/run.py
```
This compiles Qt resources and runs the application.

### Building the Application (Distribution)
```bash
uv run scripts/build.py
```
This creates a standalone executable in `dist/`.

### Compiling Qt Resources Only
Resources are auto-compiled by run/build scripts, but to compile manually:
```bash
uv run pyside6-rcc resources.qrc -o src/slide_voice_app/rc_resources.py
```

### Running Tests
```bash
uv run pytest                           # Run all tests
uv run pytest tests/test_file.py        # Run specific test file
uv run pytest tests/test_file.py::test_name  # Run single test
uv run pytest -k "pattern"              # Run tests matching pattern
uv run pytest -x                        # Stop on first failure
```

### Linting and Formatting
```bash
uv run ruff check .                     # Run linter
uv run ruff check . --fix               # Auto-fix lint issues
uv run ruff format .                    # Format code
uv run pyright                          # Type checking
```

## Code Style Guidelines

### Python Code Style

1. **Formatting:** Use `ruff format` for consistent formatting (Black-compatible)
2. **Line Length:** 88 characters maximum
3. **Quotes:** Double quotes for strings
4. **Trailing Commas:** Use trailing commas in multi-line structures

### Import Organization

Order imports as follows, separated by blank lines:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import subprocess
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from slide_voice_app.utils import helper_function
```

### Type Annotations

- Use type hints for all function parameters and return values
- Use `from __future__ import annotations` for forward references
- Use `typing` module types when needed (`Optional`, `Union`, `List`, etc.)

```python
def process_file(path: Path, options: dict[str, str] | None = None) -> bool:
    """Process a file with optional configuration."""
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions/Methods | snake_case | `compile_resources()` |
| Variables | snake_case | `file_path` |
| Classes | PascalCase | `SlideManager` |
| Constants | UPPER_SNAKE_CASE | `BASE_DIR` |
| Private | Leading underscore | `_internal_method()` |
| Module | snake_case | `slide_parser.py` |

### Error Handling

- Use specific exception types, not bare `except:`
- Provide meaningful error messages
- Log errors appropriately before re-raising or exiting

```python
try:
    result = subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"Command failed: {e}")
    sys.exit(1)
```

### Docstrings

Use Google-style docstrings:

```python
def load_presentation(path: Path) -> Presentation:
    """Load a PowerPoint presentation from disk.

    Args:
        path: Path to the .pptx file.

    Returns:
        A Presentation object with parsed slides.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file is not a valid .pptx.
    """
```

## PySide6 / QML Guidelines

1. **Resource Management:**
   - Use `resources.qrc` for shipping QML and assets
   - Access resources via `:/` prefix (e.g., `:/ui/Main.qml`)
   - Add new QML files to `resources.qrc` with appropriate aliases

2. **Generated Files:**
   - `rc_resources.py` is auto-generated - never edit manually
   - This file is in `.gitignore`

3. **QML File Structure:**
   - Place QML files in `src/slide_voice_app/ui/`
   - Use descriptive component names (PascalCase)

4. **Importing Resources:**
   - Import the resource module to register resources:
   ```python
   import slide_voice_app.rc_resources  # noqa: F401
   ```

## Documentation

- **Developer docs:** `docs/dev/` - Architecture, design decisions, API docs
- **User docs:** `docs/user/` - Installation, usage guides, tutorials

Keep documentation updated when making changes to the codebase.
