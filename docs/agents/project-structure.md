# Project Structure

Repository layout

```
slide-voice-app/
├── src/slide_voice_app/     # Main application source code
│   ├── __main__.py          # Application entry point
│   ├── ui/                  # QML files for UI
│   ├── qml_modules/         # QML module outputs (qmldir, qml, qmltypes)
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
