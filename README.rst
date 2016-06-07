***********
namedtuple2
***********

A drop in replacement for the standard function `collections.namedtuple` with
the following benefits:

- `Memoization`_ on the generated type.
- Additional `Docstring`_ argument.
- Can be used:
    - `Like the standard collections.namedtuple`_
    - `As a function decorator`_
    - `As a function decorator factory`_
    - `As a class decorator`_
    - `As a class decorator factory`_
- When used as a decorator the type name does not have to be specified twice.

=====
Usage
=====

----------------------------------------
Like the standard collections.namedtuple
----------------------------------------

    >>> from namedtuple_decorator import namedtuple
    >>> Point3 = namedtuple('Point3', 'x y z')

-----------------------
As a function decorator
-----------------------

    >>> from namedtuple_decorator import namedtuple
    >>> @namedtuple
    ... def Point3(x, y, z):
    ...     """an element of some set called a space"""

-------------------------------
As a function decorator factory
-------------------------------

If the field names are dynamically generated, they can be passed to the
decorator factory:

    >>> from namedtuple_decorator import namedtuple
    >>> @namedtuple(chr(x) for x in range(120, 123))
    ... def Fields(*args):
    ...     pass

--------------------
As a class decorator
--------------------

    >>> from namedtuple_decorator import namedtuple
    >>> @namedtuple(chr(x) for x in range(120, 123))
    ... class Point3:
    ...     """an element of some set called a space"""
    ...     def __init__(self, x, y, z):
    ...         pass

----------------------------
As a class decorator factory
----------------------------

If the field names are dynamically generated, they can be passed to the
decorator factory:

    >>> from namedtuple_decorator import namedtuple
    >>> @namedtuple(chr(x) for x in range(120, 123))
    ... class Fields:
    ...     def __init__(self, *args):
    ...         pass

=========
Docstring
=========

TODO

===========
Memoization
===========

The generated classes are memoized which is particularly useful when generating
named tuples with dymamic field names to ensure that lots of classes are not
instantiated. See the examples/csv_named_tuple_reader.py for an demonstration
of how this might be useful.

==========
Motivation
==========

The main motivation for this is to provide an improved syntax for defining a
named tuple, as well as offering the ability to set the docstring on the newly
created type.

============
How it works
============

The functio-n namedtuple selects an implementation based on the parameters that
are passed:

- when given a class we assume that a plain class decorator is intended
- when given a callable we assume that a plain function decorator is intended
    - the function should return either the field_names as expected in
      collections.namedtuple
    - or None in which case the function argument names are used as the
      field_names
- when fields_names is present in keyword arguments, or the second positional
  argument is iterable we assume the classic form of namedtuple is intended
- otherwise we assume a decorator factory is desired with the verbose and
  replace flags passed as arguments.

====
TODO
====

- Better docstrings (by monkey patching _class_template)
- Only rename > 2.7
- Signature in python3 instead of getargspec
- Sphinx, readthedocs
- travis, appveyor, circle
- setup.py pypi
- test with tox
- Add test for memoize function
- Find some way of only displaying the output when verbose==True
- Don't lose additional methods in class decorator? Maybe create a class that is a child of the namedtuple
- Add some documentation info about the philosophy behind define the signature
- take a look at some alternative memoize implementations and use the best (see http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/ and https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize)