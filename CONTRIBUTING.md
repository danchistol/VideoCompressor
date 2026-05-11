# Contributing

Contributions are welcome.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Development guidelines

- Keep the GUI simple and beginner-friendly.
- Avoid committing generated videos or large media files.
- Test with at least one short video before opening a pull request.
- Keep changes focused and describe them clearly in the pull request.

## Suggested checks

```bash
python -m py_compile VideoCompressor.py
```
