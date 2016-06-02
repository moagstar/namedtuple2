# namedtuple_decorator

A drop in replacement for the standard function collections.namedtuple that
supports use as a class and function decorator, while still supporting the
standard usage:

```python
@namedtuple
class Point:
    '''an element of some set called a space'''
    _fields = 'x y'

@namedtuple
def Point():
    '''an element of some set called a space'''
    return 'x y'

Point = namedtuple('Point', 'x y')
```

The replacement function also gives the ability to set the docstring of the
created type.

The replace and verbose parameters are supported as parameters to the
decorator, for example:

```python
@namedtuple(replace=True)
def Point():
    return xrange(10)
```

## Installation

Installing from PyPI using pip:

```bash
$ pip install table2dicts
```

Installing from source:

```bash
$ python setup.py install
```

## Motivation

The main motivation for this is to provide an improved syntax for defining a
named tuple, as well as offering the ability to set the docstring on the newly
created type.

## How it works

The function namedtuple selects an implementation based on the parameters that
are passed:

* when given a class we assume that a plain class decorator is intended
* when given a callable we assume that a plain function decorator is intended
* when fields_names is present in keyword arguments, or the second positional
  argument is iterable we assume the classic form of namedtuple is intended
* otherwise we assume a decorator factory is desired with the verbose and
  replace flags passed as arguments.