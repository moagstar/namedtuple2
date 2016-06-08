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
def _memoized_namedtuple(name, field_names, verbose, rename):
    return _original_namedtuple(name, field_names, verbose, rename)


def _namedtuple(name, field_names, verbose=False, rename=False):
    # when verbose was requested we should still display the generated code
    # at the moment the best way I can do this is by regenerating the type
    # even though it has been cached...
    if verbose:
        return _original_namedtuple(name, field_names, verbose, rename)
    else:
        return _memoized_namedtuple(name, field_names, verbose, rename)


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


def _namedtuple_from_func(name, field_names, verbose, rename, __doc__):
    nt = _namedtuple(name, field_names, verbose, rename)
    doc_dict = {'__doc__': __doc__ or nt.__doc__}
    return type(name, (nt,), doc_dict)


def _class_decorator(cls, field_names, verbose, rename):
    """
    Decorate a class to make it into a named tuple.
    """
    # strip off self
    field_names = field_names or inspect.getargspec(cls.__init__).args[1:]
    return _namedtuple_from_func(cls.__name__, field_names, verbose, rename,
                                 cls.__doc__)


def _function_decorator(fn, field_names, verbose, rename):
    """
    Decorate a function to make it into a named tuple.
    """
    field_names = field_names or inspect.getargspec(fn).args
    return _namedtuple_from_func(fn.__name__, field_names, verbose, rename,
                                 fn.__doc__)


def _decorator(o, field_names, verbose, rename):
    """
    Decorate an object to make it into a named tuple, selecting the
    appropriate decorator based on the type of the object o.
    """
    if inspect.isclass(o):
        return _class_decorator(o, field_names, verbose, rename)
    else:
        return _function_decorator(o, field_names, verbose, rename)


def _check_kwargs(**kwargs):
    supported_kwargs = {'rename', 'verbose'}
    if kwargs:
        other_kwargs = supported_kwargs | set(kwargs.keys())
        if other_kwargs != supported_kwargs:
            unexpected_kwargs = other_kwargs - supported_kwargs
            fmt = "namedtuple() got an unexpected keyword argument '%s'"
            msg = fmt % unexpected_kwargs.pop()
            raise TypeError(msg)


def namedtuple(*args, **kwargs):
    """
    """
    _check_kwargs(**kwargs)

    # used as a plain class decorator
    if _is_used_as_plain_class_decorator(*args):
        return _class_decorator(args[0], None, False, False)

    # used as a plain function decorator
    elif _is_used_as_plain_function_decorator(*args):
        return _function_decorator(args[0], None, False, False)

    # used like the standard python namedtuple
    elif _is_used_like_std_namedtuple(*args, **kwargs):
       return _namedtuple(*args, **kwargs)

    # used as a parameterized decorator
    else:
        verbose = kwargs.get('verbose', False)
        rename = kwargs.get('rename', False)
        field_names = args[0] if args else None
        return functools.partial(_decorator, field_names=field_names,
                                 verbose=verbose, rename=rename)
