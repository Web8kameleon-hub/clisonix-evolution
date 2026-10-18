# Publishing CLX

## Build

```bash
cd sdk/python/clx
python -m pip install --upgrade build twine
python -m build
```

## Validate

```bash
twine check dist/*
python -m pytest hotguard/test_scanner_printer.py -q
```

## TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

## PyPI

```bash
python -m twine upload dist/*
```

## Release Rules

- Publish to TestPyPI first.
- Do not publish if tests fail.
- Do not publish if no-fake-data guarantees were weakened.
- Tag the matching git release after package verification.
