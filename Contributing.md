# Contributing

## Setup

1. Clone the repository
2. pip install poetry
3. poetry install --with dev
4. eval $(poetry env activate)
5. pre-commit install

## Activate the virtual environment

```bash
eval $(poetry env activate)
```

## API reference

The pages in `docs/api/` are generated from the source code. After changing a class, a method signature,
a docstring or an enum, regenerate them (a unit test fails while they are out of date):

```bash
python docs/generate_api_docs.py
```

## ChangeLog

When you make code changes, please document them in the ChangeLog. You can use the [Keep a Changelog assistant](https://chatgpt.com/g/g-684af39084148191b7c83c89daf1b477-keep-a-changelog-assistant) or Claude Code to help write the entry.
