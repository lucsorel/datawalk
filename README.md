# Datawalk

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lucsorel/datawalk/main.svg)](https://results.pre-commit.ci/latest/github/lucsorel/datawalk/main)

Fetch values from nested data structures.

## Features

```python
walk_1_1 = Walk / 'attribute_1' / 'attribute_1_1'
# use ellipsis to move 1 step back
walk_1_2 = walk_1_1 / ... / 'attribute_1_2'
```
