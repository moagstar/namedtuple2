# std
import imp
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import inspect
import functools
import pickle
import base64
# namedtuple3
from _namedtuple_impl import namedtuple as _original_namedtuple


def _b32encode_no_digits(s, dumps=pickle.dumps):
    encoded = base64.b32encode(dumps(s))
    return ''.join(
        chr(ord('a') + int(x)) if x.isdigit() else ('_' if x == '=' else x)
        for x in encoded
    )


def _b32decode_no_digits(s, loads=pickle.loads):
    string_to_decode = ''.join(
        '=' if x == '_' else (str(ord(x) - ord('a')) if x.islower() else x)
        for x in s
    )
    return loads(base64.b32decode(string_to_decode))


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


@memoize
def _memoized_namedtuple(name, field_names, verbose, rename, docstring):
    """
    Named tuple function which remembers the resulting type based on the
    parameters passed.
    """
    return _original_namedtuple(name, field_names, verbose, rename, docstring)


def _namedtuple(name, field_names, verbose=False, rename=False, docstring=None):
    # when verbose was requested we should still display the generated code
    # at the moment the best way I can do this is by regenerating the type
    # even though it has been cached...
    if verbose:
        return _original_namedtuple(name, field_names, verbose, rename, docstring)
    else:
        return _memoized_namedtuple(name, field_names, verbose, rename, docstring)


def _isiterable(o):
    """
    :return: True if o is iterable, otherwise False
    """
    try:
        iter(o)
        return True
    except:
        return False


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
    ...     def __init__(self, x, y):
    ...         pass
    """
    return len(args) == 1 and inspect.isclass(args[0])


def _class_decorator(cls, field_names, verbose, rename, docstring):
    """
    Create a namedtuple from a decorated class.
    """
    # strip off self from the args
    field_names = field_names or inspect.getargspec(cls.__init__).args[1:]
    docstring = docstring or cls.__doc__
    return _namedtuple(cls.__name__, field_names, verbose, rename, docstring)


def _function_decorator(fn, field_names, verbose, rename, docstring):
    """
    Decorate a function to make it into a named tuple.
    """
    field_names = field_names or inspect.getargspec(fn).args
    docstring = docstring or fn.__doc__
    return _namedtuple(fn.__name__, field_names, verbose, rename, docstring)


def _decorator(o, field_names, verbose, rename, docstring):
    """
    Decorate an object to make it into a named tuple, selecting the
    appropriate decorator based on the type of the object o.
    """
    if inspect.isclass(o):
        return _class_decorator(o, field_names, verbose, rename, docstring)
    else:
        return _function_decorator(o, field_names, verbose, rename, docstring)


def _check_kwargs(**kwargs):
    supported_kwargs = {'rename', 'verbose', 'docstring'}
    if kwargs:
        other_kwargs = supported_kwargs | set(kwargs.keys())
        if other_kwargs != supported_kwargs:
            unexpected_kwargs = other_kwargs - supported_kwargs
            fmt = "namedtuple() got an unexpected keyword argument '%s'"
            msg = fmt % unexpected_kwargs.pop()
            raise TypeError(msg)


def namedtuple(*args, **kwargs):
    """
    Returns a new subclass of tuple with named fields.

    This is a drop in replacement for the standard function
    :code:`collections.namedtuple` which can be used as a decorator so that the
    type name does not have to be written twice:

        >>> from namedtuple3 import namedtuple
        >>> @namedtuple
        ... def Point3(x, y, z) : 'an element of a set named a space'

    vs:

        >>> from collections import namedtuple
        >>> Point3 = namedtuple('Point3', 'x y z')

    """
    _check_kwargs(**kwargs)

    # used as a plain class decorator
    if _is_used_as_plain_class_decorator(*args):

        return _class_decorator(args[0], field_names=None, verbose=False,
                                rename=False, docstring=None)

    # used as a plain function decorator
    elif _is_used_as_plain_function_decorator(*args):

        return _function_decorator(args[0], field_names=None, verbose=False,
                                   rename=False, docstring=None)

    # used like the standard python namedtuple
    elif _is_used_like_std_namedtuple(*args, **kwargs):
       return _namedtuple(*args, **kwargs)

    # used as a parameterized decorator
    else:
        verbose = kwargs.get('verbose', False)
        rename = kwargs.get('rename', False)
        docstring = kwargs.get('docstring', None)
        field_names = args[0] if args else None

        return functools.partial(_decorator, field_names=field_names,
                                 verbose=verbose, rename=rename,
                                 docstring=docstring)
