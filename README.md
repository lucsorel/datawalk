# Datawalk

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lucsorel/datawalk/main.svg)](https://results.pre-commit.ci/latest/github/lucsorel/datawalk/main)

Fetch values from nested data structures with a friendly syntax based on math operators.

The features provided by this library are inspired by the [pathlib.Path](https://docs.python.org/3/library/pathlib.html) API proposing to use "/" operators to represent the folder structure to a file.
Datawalk proposes to use similar operators to access a value in a nested data structure.
A path to a value is called a `walk`.

Design choices and implementation rely on these documentation pages:
- operators and special methods: https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
- operator precedence: https://docs.python.org/3/reference/expressions.html#operator-precedence

Benefits from using a walk to retrieve a value:
- walks provide an expressive way of navigating in data structures, hoping to improve legibility
- a walk is an indirection, providing a way to decouple the logic to retrieve a value from the logic to manipulate the value.
It can be helpfull when you are refactoring the structure of your data: change the walk but not your business logic
- when writing a walk, the syntax is the same when using dict keys or object attributes or sequence indices
- walks are immutable and are agnostic of data sources, they can be applied to different datastructures.
They can also be combined to produce deeper walks
- a walk provides expressive error messages telling where it failed to retrieve a value

Jump to the Use-cases section to see it in action.

## Installation

Install `datawalk` with your favorite Python package manager:

```sh
# install from PyPI
pip install datawalk

uv add datawalk

poetry add datawalk
# etc.

# install from Github
pip install git+https://github.com/lucsorel/datawalk.git#egg=datawalk

uv add "datawalk @ git+https://github.com/lucsorel/datawalk"

poetry add git+https://github.com/lucsorel/datawalk.git
# etc.
```

## Use cases

Let's create a nested data structure combining lists, dictionnaries, classes, dataclasses and namedtuples:

```python
class Pet:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

@dataclass
class PetDataclass:
    name: str
    type: str

class PetNamedTuple(NamedTuple):
    name: str
    type: str

data = {
    'name': 'Lucie Nation',
    'org': {
        'title': 'Datawalk',
        'address': {'country': 'France'},
        'phones': ['01 23 45 67 89', '02 13 46 58 79'],
        (666, 'ev/l'): 'hashable key',
    },
    'friends': [
        {'name': 'Frankie Manning'},
        {'name': 'Harry Cover'},
        {'name': 'Suzie Q', 'phone': '06 43 15 27 98'},
        {'name': 'Jean Blasin'},
    ],
    'pets': [
        Pet('Cinnamon', 'cat'),
        PetDataclass('Caramel', 'dog'),
        Pet('Melody', 'bird'),
        PetNamedTuple('Socks', 'cat'),
    ],
}
```

Some use-cases:

```python
from datawalk import Walk

name_walk = Walk / 'name'
name_walk.walk(data) # -> 'Lucie Nation'
# variations (the | pipe operator calls the .walk() method):
name_walk | data     # -> 'Lucie Nation'
Walk / 'name' | data # -> 'Lucie Nation'

# use default value when failing to retrieve a value (with the ^ operator)
(Walk / 'lastname').walk(data, default=None) # -> None
Walk / 'lastname' ^ (data, None)             # -> None

# organisation country
Walk / 'org' / 'address' / 'country' | data # -> 'France'
# combine walks
org_walk = Walk / 'org'
country_walk = Walk / 'address' / 'country'
org_walk + country_walk | data # -> 'France'

# get the 2nd org phone number
org_walk / 'phones' / 1 | data # -> '02 13 46 58 79'

# filter lists
# - by slicing
Walk / 'pets' / slice(::2) | data # -> [cinnamon, melody] Pet instances
# - by targeting the first instance matching a key:value requirement
Walk / 'pets' @ ('type', 'dog') / 'name' | data # -> 'Caramel'
# - by targeting all instances whose key matches a list of values
Walk / 'pets' % ('name', ['Melody', 'Socks']) | data # -> [melody, socks] instances

# use ellipsis to create a walk without the last selector
suzie_name_walk = Walk / 'friends' @ ('name', 'Suzie Q') / 'name'
suzie_phone_walk = suzie_name_walk / ... / 'phone'
suzie_name_walk | data  # -> 'Suzie Q'
suzie_phone_walk | data # -> '06 43 15 27 98'

# walk representations are concise and expressive
repr(suzie_phone_walk)         # -> '.friends @(name==Suzie Q) .phone'
repr(org_walk / 'phones' / 1) # -> '.org .phones [1]'
repr(Walk / 'pets' / % ('name', ['Melody', 'Socks'])) # -> ".pets %(name in ['Melody', 'Socks']"
```

Datawalk helps you fix your walks with explicit error messages:

```python
Walk / 'friends' @ ('name', 'Suzie Q') / 'phone_number' | data
# WalkError: datawalk.errors.WalkError: walked [.friends, @(name==Suzie Q)] but could not find .phone_number in {'name': 'Suzie Q', 'phone': '06 43 15 27 98'}

Walk / 'pets' @ ('name', 'Vanilla') / 'name' | data
# WalkError: walked [.pets] but could not find @(name==Vanilla) in (Pet(name=Cinnamon, type=cat), PetDataclass(name='Caramel', type='dog'), Pet(name=Melody, type=bird), PetNamedTuple(name='Socks', type='cat'))",

Walk / 'pets' % ('type', 'cat') # should have been % ('type', ['cat'])
# SelectorError: unsupported filter: ('type', 'cat'), value cat must be a sequence
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

# Changelog

See [CHANGELOG.md](CHANGELOG.md).

# Licence

Unless stated otherwise all works are licensed under the [MIT license](http://spdx.org/licenses/MIT.html), a copy of which is included [here](LICENSE).

# Contributions

I'm thankful to [all the people who have contributed](https://github.com/lucsorel/datawalk/graphs/contributors) to this project:

![](https://contrib.rocks/image?repo=lucsorel/datawalk)

## Pull requests

Pull-requests are welcome and will be processed on a best-effort basis.

Pull requests must follow the guidelines enforced by the `pre-commit` hooks:

- commit messages must follow the Angular conventions enforced by the `commitlint` hook
- code formatting must follow the conventions enforced by the `isort` and `ruff-format` hooks
- code linting should not detect code smells in your contributions, this is checked by the `ruff` hooks

## Code conventions

The code conventions are described and enforced by [pre-commit hooks](https://pre-commit.com/hooks.html) to maintain consistency across the code base.
The hooks are declared in the [.pre-commit-config.yaml](.pre-commit-config.yaml) file.

Set the git hooks (`pre-commit` and `commit-msg` types):

```sh
uv run pre-commit install
```

Before committing, you can check your changes with:

```sh
# put all your changes in the git staging area
git add -A

# all hooks
uv run pre-commit run --all-files

# a specific hook
uv run pre-commit run ruff-format --all-files
```
