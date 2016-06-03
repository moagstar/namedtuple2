import collections
import inspect
import functools


def memoize(obj):
    """
    Cache the result of a function call based on it's arguments.
    """
    cache = obj.cache = {}
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


_original_namedtuple = collections.namedtuple


@memoize
def _memoized_namedtuple(name, field_names, verbose, *args):
    return _original_namedtuple(name, field_names, verbose, *args)


def _namedtuple(name, field_names, verbose, *args):
    # when verbose was requested we should still display the generated code
    # at the moment the best way I can do this is by regenerating the type
    # even though it has been cached...
    if verbose:
        return _original_namedtuple(name, field_names, verbose, *args)
    else:
        return _memoized_namedtuple(name, field_names, verbose, *args)


def _isiterable(o):
    """
    :return: True if o is iterable, otherwise False
    """
    try:
        iter(o)
        return True
    except:
        return False


def _get_verbose_rename(*args, **kwargs):
    """
    Get the verbose and rename arguments from positional and keyword arguments
    passed to the decorator.
    """
    verbose = kwargs.get('verbose', False)
    rename = kwargs.get('rename', False)

    if len(args) == 1:
        verbose = args[0]
    elif len(args) == 2:
        verbose = args[0]
        rename = args[1]

    return verbose, rename


def _is_used_like_std_namedtuple(*args, **kwargs):
    """
    Determine if namedtuple is called as a normal function like the standard
    way of defining namedtuple, e.g.

    >>> Point = namedtuple('Point', 'x y')
    """
    return 'field_names' in kwargs or (len(args) > 1 and _isiterable(args[1]))


def _is_used_as_plain_function_decorator(*args):
    """
    Determine if the decorator is used as a plain class decorator, without
    parameters e.g.

    >>> @namedtuple
    ... def Point(x, y):
    ...     pass
    """
    return len(args) == 1 and callable(args[0])


def _is_used_as_plain_class_decorator(*args):
    """
    Determine if the decorator is used as a plain class decorator, without
    parameters e.g.

    >>> @namedtuple
    ... class Point:
    ...     _fields = 'x y'
    """
    return len(args) == 1 and inspect.isclass(args[0])


def _class_decorator(verbose, rename, cls):
    """
    Decorate a class to make it into a named tuple.
    """
    nt = _namedtuple(cls.__name__, cls._fields, verbose, rename)
    doc_dict = {'__doc__': cls.__doc__ or nt.__doc__}
    return type(cls.__name__, (nt,), doc_dict)


def _function_decorator(verbose, rename, fn):
    """
    Decorate a function to make it into a named tuple.
    """
    args = inspect.getargspec(fn).args
    fields = fn(*args) or args
    nt = _namedtuple(fn.__name__, fields, verbose, rename)
    doc_dict = {'__doc__': fn.__doc__ or nt.__doc__}
    return type(fn.__name__, (nt,), doc_dict)


def _decorator(verbose, rename, o):
    """
    Decorate an object to make it into a named tuple, selecting the
    appropriate decorator based on the type of the object o.
    """
    if inspect.isclass(o):
        return _class_decorator(verbose, rename, o)
    else:
        return _function_decorator(verbose, rename, o)


def namedtuple(*args, **kwargs):
    """
    Returns a new tuple subclass named typename. The new subclass is used to
    create tuple-like objects that have fields accessible by attribute lookup
    as well as being indexable and iterable. Instances of the subclass also
    have a helpful docstring (with typename and field_names) and a helpful
    __repr__() method which lists the tuple contents in a name=value format.

    The field_names are a sequence of strings such as ['x', 'y'].
    Alternatively, field_names can be a single string with each fieldname
    separated by whitespace and/or commas, for example 'x y' or 'x, y'.

    Any valid Python identifier may be used for a fieldname except for names
    starting with an underscore. Valid identifiers consist of letters, digits,
    and underscores but do not start with a digit or underscore and cannot be
    a keyword such as class, for, return, global, pass, print, or raise.

    If rename is True, invalid fieldnames are automatically replaced with
    positional names. For example, ['abc', 'def', 'ghi', 'abc'] is converted
    to ['abc', '_1', 'ghi', '_3'], eliminating the keyword def and the
    duplicate fieldname abc.

    If verbose is True, the class definition is printed just before being built.

    Named tuple instances do not have per-instance dictionaries, so they are
    lightweight and require no more memory than regular tuples.

    For Example:

    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)

    namedtuple can also be used as a function or class decorator, which allows
    for a nicer syntax where the name does not have to be repeated.

    >>> @namedtuple
    ... def Point(x, y): pass
    >>> p = Point(11, y=22)
    >>> p.x + p.y
    33

    When used as a class decorator the class should have a _fields member which
    defines the fields of the namedtuple. The _fields member should be a
    sequence of strings such as ['x', 'y']. Alternatively, field_names can be
    a single string with each fieldname separated by whitespace and/or commas,
    for example 'x y' or 'x, y'.

    >>> @namedtuple
    ... class Point:
    ...     _fields = 'x y'
    >>> p = Point(11, y=22)
    >>> p[0] + p[1]
    33

    Both the class and function decorators also support the verbose and rename
    parameters:

    >>> @namedtuple(rename=True)
    ... class Point:
    ...     _fields = 'x 1'
    >>> p = Point(11, _1=22)
    >>> p._1
    22
    >>> @namedtuple(rename=True)
    ... def Point:
    ...     return 'x 1'
    >>> p = Point(11, _1=22)
    >>> p._1
    22

    When used as a decorator the named tuple can also specify a docstring:

    >>> @namedtuple
    ... class Point:
    ...     '''an element of some set called a space'''
    ...     _fields = 'x y'
    >>> Point.__doc__
    'an element of some set called a space'

    You should not define additional members or functions since these will be
    lost:

    >>> @namedtuple
    ... class Point:
    ...     def method(self):
    ...         pass
    ...     _fields = 'x y'
    >>> point = Point(11, y=22)
    >>> hasattr(point, 'method')
    False
    """
    # used as a plain class decorator
    if _is_used_as_plain_class_decorator(*args):
        return _class_decorator(False, False, args[0])

    # used as a plain function decorator
    elif _is_used_as_plain_function_decorator(*args):
        return _function_decorator(False, False, args[0])

    # used like the standard python namedtuple
    elif _is_used_like_std_namedtuple(*args, **kwargs):
        return _original_namedtuple(*args, **kwargs)

    # used as a parameterized decorator
    else:
        verbose, rename = _get_verbose_rename(*args, **kwargs)
        return functools.partial(_decorator, verbose, rename)
