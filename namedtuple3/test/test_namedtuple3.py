# std
import collections
import contextlib
import itertools
import uuid
# six
from six import StringIO
# mock
import mock
# pytest
import pytest
# namedtuple_decorator
from namedtuple3 import namedtuple
from namedtuple3._namedtuple3_impl import (
    _is_used_as_plain_class_decorator,
    _is_used_as_plain_function_decorator,
    _isiterable,
    _is_used_like_std_namedtuple,
    _check_kwargs,
)


# helpers ######################################################################

def _verify(nt, doc_expected=None, field_names=('x', 'y', 'z')):

    expected = collections.OrderedDict()
    expected[field_names[0]] = 2
    expected[field_names[1]] = 4
    expected[field_names[2]] = 8

    kwargs = expected
    args = expected.values()

    assert nt(*args)._asdict() == expected
    assert nt(**kwargs)._asdict() == expected

    doc_fields_expected = str(nt._fields).replace("'", '')
    doc_expected = doc_expected or (nt.__name__ + doc_fields_expected)
    assert nt.__doc__ == doc_expected


def verify_point3(nt):
    _verify(nt)


def verify_fields(nt):
    _verify(nt, field_names=('_0', '_1', '_2'))


def verify_point3_with_docstring(nt):
    _verify(nt, doc_expected='an element of some set called a space',
           field_names=('x', 'y', 'z'))


def verify_fields_with_docstring(nt):
    _verify(nt, doc_expected='an element of some set called a space',
           field_names=('_0', '_1', '_2'))


@contextlib.contextmanager
def should_have_verbose_output(expected):
    yield
    # stream = StringIO()
    # with mock.patch('sys.stdout', stream):
    #     yield
    # if expected:
    #     assert len(stream.getvalue())
    # else:
    #     assert not len(stream.getvalue())
    # assert sys.stdout != stream


@contextlib.contextmanager
def should_raise_value_error(should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            yield
    else:
        yield


# impl functions ###############################################################

def test_isiterable():
    assert _isiterable([]) == True
    assert _isiterable('') == True
    assert _isiterable((1, 2,)) == True
    assert _isiterable((x for x in range(1))) == True   # pragma: no cover - generator expression never iterated
    assert _isiterable(test_isiterable) == False
    assert _isiterable(True) == False
    assert _isiterable(False) == False
    assert _isiterable(1) == False
    assert _isiterable(0) == False
    assert _isiterable(None) == False


def test_is_used_like_std_namedtuple():

    args = []
    kwargs = {'field_names': ''}
    assert _is_used_like_std_namedtuple(*args, **kwargs)

    args = ['Person']
    kwargs = {'field_names': ''}
    assert _is_used_like_std_namedtuple(*args, **kwargs)

    args = ['Person', 'a b c']
    kwargs = {}
    assert _is_used_like_std_namedtuple(*args, **kwargs)

    args = []
    kwargs = {'verbose': True}
    assert not _is_used_like_std_namedtuple(*args, **kwargs)

    args = [True]
    kwargs = {'rename': True}
    assert not _is_used_like_std_namedtuple(*args, **kwargs)

    args = [True, True]
    kwargs = {}
    assert not _is_used_like_std_namedtuple(*args, **kwargs)


def test_is_used_as_plain_class_decorator():

    args = []
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True]
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True, True]
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True]
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True]
    assert not _is_used_as_plain_class_decorator(*args)

    args = ['Person', 'a b c']
    assert not _is_used_as_plain_class_decorator(*args)

    class A:
        def __init__(self): pass

    args = [A]
    assert _is_used_as_plain_class_decorator(*args)

    args = [A, A]
    assert not _is_used_as_plain_class_decorator(*args)


def test_is_used_as_plain_function_decorator():

    args = []
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True]
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True, True]
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True]
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True]
    assert not _is_used_as_plain_function_decorator(*args)

    args = ['Person', 'a b c']
    assert not _is_used_as_plain_function_decorator(*args)

    def a(): pass  # pragma: no cover - function never called

    args = [a]
    assert _is_used_as_plain_function_decorator(*args)

    args = [a, a]
    assert not _is_used_as_plain_function_decorator(*args)


def test_check_kwargs():

    with pytest.raises(TypeError):
        _check_kwargs(apples='oranges')

    with pytest.raises(TypeError):
        _check_kwargs(verbose=True, apples='oranges')

    with pytest.raises(TypeError):
        _check_kwargs(rename=True, apples='oranges')

    with pytest.raises(TypeError):
        _check_kwargs(rename=True, verbose=True, apples='oranges')

    _check_kwargs()
    _check_kwargs(verbose=True)
    _check_kwargs(rename=True)
    _check_kwargs(verbose=True, rename=True)


# memoize ######################################################################

def test_memoize():

    call_count = [0]

    def nametuple_replace(*args, **kwargs):
        call_count[0] += 1
        return collections.namedtuple(*args, **kwargs)

    @mock.patch('namedtuple3._namedtuple3_impl._original_namedtuple',
                nametuple_replace)
    def do_test():
        """verify that multiple classes are not created"""
        unique = str(uuid.uuid4())
        type_name = '_' + unique.replace('-', '_')
        field_names = unique.replace('-', ' ')
        for i in xrange(5):
            t = namedtuple(type_name, field_names, rename=True)

    do_test()
    assert call_count[0] == 1


# standard function: basic #####################################################

def test_standard_function():

    Point3 = namedtuple('Point3', 'x, y, z')

    verify_point3(Point3)


@pytest.mark.parametrize("verbose", [True, False])
def test_standard_function_verbose(verbose):

    Point3 = namedtuple('Point3', 'x, y, z', verbose=verbose)

    verify_point3(Point3)


@pytest.mark.parametrize("rename", [True, False])
def test_standard_function_rename(rename):

    Point3 = namedtuple('Point3', 'x, y, z', rename=rename)

    verify_point3(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_standard_function_verbose_and_rename(verbose, rename):

    Point3 = namedtuple('Point3', 'x, y, z', verbose=verbose, rename=rename)

    verify_point3(Point3)


# function decorator: basic ####################################################

def test_function_decorator():

    @namedtuple
    def Point3(x, y, z):
        """an element of some set called a space"""

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose", [True, False])
def test_function_decorator_verbose(verbose):

    @namedtuple(verbose=verbose)
    def Point3(x, y, z):
        """an element of some set called a space"""

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("rename", [True, False])
def test_function_decorator_rename(rename):

    @namedtuple(rename=rename)
    def Point3(x, y, z):
        """an element of some set called a space"""

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_function_decorator_verbose_and_rename(verbose, rename):

    @namedtuple(verbose=verbose, rename=rename)
    def Point3(x, y, z):
        """an element of some set called a space"""
        
    verify_point3_with_docstring(Point3)


# class decorator: basic #######################################################

def test_class_decorator():

    @namedtuple
    class Point3:
        """an element of some set called a space"""
        def __init__(self, x, y, z):
            pass

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose", [True, False])
def test_class_decorator_verbose(verbose):

    @namedtuple(verbose=verbose)
    class Point3:
        """an element of some set called a space"""
        def __init__(self, x, y, z):
            pass

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("rename", [True, False])
def test_class_decorator_rename(rename):

    @namedtuple(rename=rename)
    class Point3:
        """an element of some set called a space"""
        def __init__(self, x, y, z):
            pass

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_class_decorator_verbose_and_rename(verbose, rename):

    @namedtuple(verbose=verbose, rename=rename)
    class Point3:
        """an element of some set called a space"""
        def __init__(self, x, y, z):
            pass
        
    verify_point3_with_docstring(Point3)


# function decorator: dynamic field names ######################################

def test_function_decorator_dynamic_field_names():

    @namedtuple('x y z')
    def Point3(*args):
        """an element of some set called a space"""

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose", [True, False])
def test_function_decorator_dynamic_field_names_verbose(verbose):

    @namedtuple('x, y, z', verbose=verbose)
    def Point3(*args):
        """an element of some set called a space"""

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("rename", [True, False])
def test_function_decorator_dynamic_field_names_rename(rename):

    @namedtuple('x, y, z', rename=rename)
    def Point3(*args):
        """an element of some set called a space"""

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_function_decorator_dynamic_field_names_verbose_and_rename(
        verbose, rename):

    @namedtuple('x, y, z', verbose=verbose, rename=rename)
    def Point3(*args):
        """an element of some set called a space"""

    verify_point3_with_docstring(Point3)


# function decorator: dynamic field names ######################################

def test_class_decorator_dynamic_field_names():

    @namedtuple('x y z')
    class Point3:
        """an element of some set called a space"""
        def __init__(self, *args):
            pass

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose", [True, False])
def test_class_decorator_dynamic_field_names_verbose(verbose):

    @namedtuple('x, y, z', verbose=verbose)
    class Point3:
        """an element of some set called a space"""
        def __init__(self, *args):
            pass

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("rename", [True, False])
def test_class_decorator_dynamic_field_names_rename(rename):

    @namedtuple('x, y, z', rename=rename)
    class Point3:
        """an element of some set called a space"""
        def __init__(self, *args):
            pass

    verify_point3_with_docstring(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_class_decorator_dynamic_field_names_verbose_and_rename(
        verbose, rename):

    @namedtuple('x, y, z', verbose=verbose, rename=rename)
    class Point3:
        """an element of some set called a space"""
        def __init__(self, *args):
            pass
        
    verify_point3_with_docstring(Point3)


# standard function : dynamic invalid field names ##############################

def test_standard_function_dynamic_invalid_field_names():

    with should_have_verbose_output(False), \
         should_raise_value_error(True):

        Point3 = namedtuple('Point3', range(3))
        
        verify_fields(Point3)  # pragma: no cover - may not get here due to expected error raised


@pytest.mark.parametrize("verbose", [True, False])
def test_standard_functionr_dynamic_invalid_field_names_verbose(
        verbose):

    with should_have_verbose_output(False), \
         should_raise_value_error(True):

        Point3 = namedtuple('Point3', range(3), verbose=verbose)
        
        verify_fields(Point3)  # pragma: no cover - may not get here due to expected error raised


@pytest.mark.parametrize("rename", [True, False])
def test_standard_function_dynamic_invalid_field_names_rename(rename):

    with should_have_verbose_output(False), \
         should_raise_value_error(not rename):

        Point3 = namedtuple('Point3', range(3), rename=rename)
        
        verify_fields(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_standard_function_dynamic_invalid_field_names_verbose_and_rename(
        verbose, rename):

    with should_have_verbose_output(rename and verbose), \
         should_raise_value_error(not rename):

        Point3 = namedtuple('Point3', range(3), verbose=verbose, rename=rename)

        verify_fields(Point3)


# function decorator: dynamic invalid field names ##############################

def test_function_decorator_dynamic_invalid_field_names():

    with should_have_verbose_output(False), \
            should_raise_value_error(True):

        @namedtuple(range(3))
        def Point3(*args):
            """an element of some set called a space"""

        verify_fields_with_docstring(Point3)  # pragma: no cover - may not get here due to expected error raised


@pytest.mark.parametrize("verbose", [True, False])
def test_function_decorator_dynamic_invalid_field_names_verbose(verbose):

    with should_have_verbose_output(False), \
            should_raise_value_error(True):

        @namedtuple(range(3), verbose=verbose)
        def Point3(*args):
            """an element of some set called a space"""

        verify_fields_with_docstring(Point3)  # pragma: no cover - may not get here due to expected error raised


@pytest.mark.parametrize("rename", [True, False])
def test_function_decorator_dynamic_invalid_field_names_rename(rename):

    with should_have_verbose_output(False),\
         should_raise_value_error(not rename):

        @namedtuple(range(3), rename=rename)
        def Point3(*args):
            """an element of some set called a space"""

        verify_fields_with_docstring(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_function_decorator_dynamic_invalid_field_names_verbose_and_rename(
        verbose, rename):

    with should_have_verbose_output(rename and verbose), \
                   should_raise_value_error(not rename):

        @namedtuple(range(3), verbose=verbose, rename=rename)
        def Point3(*args):
            """an element of some set called a space"""

        verify_fields_with_docstring(Point3)


# class decorator: dynamic invalid field names #################################

def test_class_decorator_dynamic_invalid_field_names():

    with should_have_verbose_output(False), \
            should_raise_value_error(True):

        @namedtuple(range(3))
        class Point3:
            """an element of some set called a space"""
            def __init__(self, *args):
                pass

        verify_fields_with_docstring(Point3)  # pragma: no cover - may not get here due to expected error raised


@pytest.mark.parametrize("verbose", [True, False])
def test_class_decorator_dynamic_invalid_field_names_verbose(verbose):

    with should_have_verbose_output(False), \
            should_raise_value_error(True):

        @namedtuple(range(3), verbose=verbose)
        class Point3:
            """an element of some set called a space"""
            def __init__(self, *args):
                pass

        verify_fields_with_docstring(Point3)  # pragma: no cover - may not get here due to expected error raised


@pytest.mark.parametrize("rename", [True, False])
def test_class_decorator_dynamic_invalid_field_names_rename(rename):

    with should_have_verbose_output(False), \
         should_raise_value_error(not rename):

        @namedtuple(range(3), rename=rename)
        class Point3:
            """an element of some set called a space"""
            def __init__(self, *args):
                pass

        verify_fields_with_docstring(Point3)


@pytest.mark.parametrize("verbose,rename",
                         itertools.product([False, True], repeat=2))
def test_class_decorator_dynamic_invalid_field_names_verbose_and_rename(
        verbose, rename):

    with should_have_verbose_output(rename and verbose), \
                   should_raise_value_error(not rename):

        @namedtuple(range(3), verbose=verbose, rename=rename)
        class Point3:
            """an element of some set called a space"""
            def __init__(self, *args):
                pass

        verify_fields_with_docstring(Point3)


# docstring ####################################################################

def test_standard_docstring():

    Point3 = namedtuple('Point3', 'x y z',
                        docstring="""an element of some set called a space""")
    verify_point3_with_docstring(Point3)


# default ######################################################################

def test_default():

    @namedtuple
    def Person(surname, name='Unknown'): 'a person is a being'

    import sys
    import socket
    import datetime
    import threading

    @namedtuple
    def LogMessage(
        message,
        message_type='info',
        server=socket.gethostname(),
        application=sys.executable,
        process=lambda: threading.current_thread().name,
        timestamp=lambda: datetime.datetime.now(),
    ) : 'message for the logging system'