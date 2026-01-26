# PySide6 / QML

Resources

- Ship QML and assets via `resources.qrc`.
- Access packaged resources via `:/` (example: `:/ui/Main.qml`).
- Add new QML files to `resources.qrc` with appropriate aliases.

QML file structure

- QML files: `src/slide_voice_app/ui/`.
- Custom modules: `src/slide_voice_app/qml_modules/<ModuleName>/`.
- Add custom modules to `scripts/utils.py` for type generation.
- Use descriptive component and module names (PascalCase).
