# Datawalk

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lucsorel/datawalk/main.svg)](https://results.pre-commit.ci/latest/github/lucsorel/datawalk/main)

Fetch values from nested data structures.

## Features

```python
walk_1_1 = Walk / 'attribute_1' / 'attribute_1_1'
# use ellipsis to move 1 step back
walk_1_2 = walk_1_1 / ... / 'attribute_1_2'
```

## Tests

```sh
# in a virtual environment
python3 -m pytest -v

# with uv
uv run pytest -v
```

Code coverage (with [missed branch statements](https://pytest-cov.readthedocs.io/en/latest/config.html?highlight=--cov-branch)):

```sh
uv run pytest -v --cov=datawalk --cov-branch --cov-report term-missing --cov-fail-under 85
```
