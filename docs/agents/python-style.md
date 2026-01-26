# Python Style

Type annotations

- Type hints for all function parameters.
- Do not add return annotation for functions returning `None`.
- Prefer modern Python typing: built-in generics (`list[str]`, `dict[str, str]`) and `X | None`.

Naming

| Type | Convention | Example |
|------|------------|---------|
| Functions/Methods | snake_case | `compile_resources()` |
| Variables | snake_case | `file_path` |
| Classes | PascalCase | `SlideManager` |
| Constants | UPPER_SNAKE_CASE | `BASE_DIR` |
| Private | Leading underscore | `_internal_method()` |
| Module | snake_case | `slide_parser.py` |

Error handling

- Use specific exception types (avoid bare `except:`).
- Provide meaningful error messages.
- Log errors before re-raising or exiting.

Docstrings

- Use Google-style docstrings.
