@echo off


echo "Install poetry"
pip install poetry

echo "Install project dependencies including dev dependencies"
poetry install --with dev

echo "Activate poetry virtual environment and open shell"
eval $(poetry env activate)

echo "Install pre-commit hooks"
pre-commit install