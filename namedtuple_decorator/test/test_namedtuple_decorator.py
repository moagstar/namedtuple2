# std
import collections
import contextlib
import importlib
import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
# pytest
import pytest
# namedtuple_decorator
from namedtuple_decorator import namedtuple
from namedtuple_decorator._namedtuple_decorator_impl import (
    _get_verbose_rename,
    _is_used_as_plain_class_decorator,
    _is_used_as_plain_function_decorator,
    _isiterable,
    _is_used_like_std_namedtuple,
)


# Helpers ######################################################################

def verify(nt, age_field_name='age', doc_expected=None):

    expected = collections.OrderedDict()
    expected['name'] = 'Daniel Bradburn'
    expected[age_field_name] = '34'

    kwargs = expected
    args = expected.values()

    assert nt(*args)._asdict() == expected
    assert nt(**kwargs)._asdict() == expected

    doc_fields_expected = str(nt._fields).replace("'", '')
    doc_expected = doc_expected or (nt.__name__ + doc_fields_expected)
    assert nt.__doc__ == doc_expected


@contextlib.contextmanager
def patch(target, new):

    tokens = target.split('.')
    target_object_name = tokens.pop()
    target_module_name = '.'.join(tokens)

    target_module = importlib.import_module(target_module_name)
    old = getattr(target_module, target_object_name)
    setattr(target_module, target_object_name, new)
    try:
        yield
    finally:
        setattr(target_module, target_object_name, old)


@contextlib.contextmanager
def should_have_verbose_output(expected):
    stream = StringIO()
    with patch('sys.stdout', stream):
        yield
    if expected:
        assert len(stream.getvalue())
    else:
        assert not len(stream.getvalue())
    assert sys.stdout != stream


# Test Impl Functions ##########################################################

def test_isiterable():
    assert _isiterable([]) == True
    assert _isiterable('') == True
    assert _isiterable((1, 2,)) == True
    assert _isiterable((x for x in range(1))) == True
    assert _isiterable(test_isiterable) == False
    assert _isiterable(True) == False
    assert _isiterable(False) == False
    assert _isiterable(1) == False
    assert _isiterable(0) == False
    assert _isiterable(None) == False


def test_get_verbose_rename():

    verbose, rename = _get_verbose_rename(**{'verbose': True})
    assert verbose, not rename

    verbose, rename = _get_verbose_rename(**{'verbose': False})
    assert not verbose, not rename

    verbose, rename = _get_verbose_rename(**{'rename': True})
    assert not verbose, rename

    verbose, rename = _get_verbose_rename(**{'rename': False})
    assert not verbose, not rename

    verbose, rename = _get_verbose_rename(*(True,), **{'rename': True})
    assert verbose, rename

    verbose, rename = _get_verbose_rename(*(False,), **{'rename': True})
    assert not verbose, rename

    verbose, rename = _get_verbose_rename(*(True, False), **{})
    assert verbose, not rename

    verbose, rename = _get_verbose_rename(*(True, True), **{})
    assert verbose, rename

    verbose, rename = _get_verbose_rename(*(False, True), **{})
    assert not verbose, rename

    verbose, rename = _get_verbose_rename(*(False, False), **{})
    assert not verbose, not rename

    verbose, rename = _get_verbose_rename(*(), **{'verbose': True})
    assert verbose, not rename

    verbose, rename = _get_verbose_rename(*(), **{'rename': True})
    assert not verbose, rename

    verbose, rename = _get_verbose_rename(*(), **{'verbose': False})
    assert not verbose, not rename

    verbose, rename = _get_verbose_rename(*(), **{'rename': False})
    assert not verbose, not rename

    verbose, rename = _get_verbose_rename(*(), **{'rename': False, 'verbose': True})
    assert verbose, not rename

    verbose, rename = _get_verbose_rename(*(), **{'rename': True, 'verbose': True})
    assert verbose, rename

    verbose, rename = _get_verbose_rename(*(), **{'rename': True, 'verbose': False})
    assert not verbose, rename

    verbose, rename = _get_verbose_rename(*(), **{'rename': False, 'verbose': False})
    assert not verbose, not rename


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
    kwargs = {'replace': True}
    assert not _is_used_like_std_namedtuple(*args, **kwargs)

    args = [True, True]
    kwargs = {}
    assert not _is_used_like_std_namedtuple(*args, **kwargs)


def test_is_used_as_plain_class_decorator():

    args = []
    kwargs = {}
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True]
    kwargs = {}
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True, True]
    kwargs = {}
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True]
    kwargs = {'verbose':True}
    assert not _is_used_as_plain_class_decorator(*args)

    args = [True]
    kwargs = {'replace':True}
    assert not _is_used_as_plain_class_decorator(*args)

    args = ['Person', 'a b c']
    kwargs = {'replace':True}
    assert not _is_used_as_plain_class_decorator(*args)

    class A:
        pass

    args = [A]
    kwargs = {}
    assert _is_used_as_plain_class_decorator(*args)

    args = [A, A]
    kwargs = {}
    assert not _is_used_as_plain_class_decorator(*args)


def test_is_used_as_plain_function_decorator():

    args = []
    kwargs = {}
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True]
    kwargs = {}
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True, True]
    kwargs = {}
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True]
    kwargs = {'verbose':True}
    assert not _is_used_as_plain_function_decorator(*args)

    args = [True]
    kwargs = {'replace':True}
    assert not _is_used_as_plain_function_decorator(*args)

    args = ['Person', 'a b c']
    kwargs = {'replace':True}
    assert not _is_used_as_plain_function_decorator(*args)

    def A(): pass

    args = [A]
    kwargs = {}
    assert _is_used_as_plain_function_decorator(*args)

    args = [A, A]
    kwargs = {}
    assert not _is_used_as_plain_function_decorator(*args)


# Plain Class Decorator ########################################################

def test_plain_class_decorator():

    with should_have_verbose_output(False):

        @namedtuple
        class Person:
            _fields = 'name age'

        verify(Person)


# Class Decorator Factory ######################################################

@pytest.mark.parametrize("verbose", [True, False])
def test_class_decorator_kwargs(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose=verbose)
        class Person:
            _fields = 'name age'

        verify(Person)


@pytest.mark.parametrize("verbose", [True, False])
def test_class_decorator_args(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose, True)
        class Person:
            _fields = 'name 1'

        verify(Person, '_1')


@pytest.mark.parametrize("verbose", [True, False])
def test_class_decorator_args_kwargs(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose, rename=True)
        class Person:
            _fields = 'name 1'

        verify(Person, '_1')


@pytest.mark.parametrize("verbose", [True, False])
def test_class_decorator_kwargs_2(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose=verbose, rename=True)
        class Person:
            _fields = 'name 1'

        verify(Person, '_1')

# Class Decorator Should Raise #################################################

def test_plain_class_decorator_should_raise():

    with pytest.raises(ValueError):

        @namedtuple
        class Person:
            _fields = 'name 1'
        

def test_class_decorator_kwargs_should_raise():

    with pytest.raises(ValueError):
    
        @namedtuple(verbose=True)
        class Person:
            _fields = 'name 1'


def test_class_decorator_args_should_raise():

    with pytest.raises(ValueError):

        @namedtuple(True, False)
        class Person:
            _fields = 'name 1'


def test_class_decorator_args_kwargs_should_raise():

    with pytest.raises(ValueError):
    
        @namedtuple(True, rename=False)
        class Person:
            _fields = 'name 1'


def test_class_decorator_kwargs_2_should_raise():

    with pytest.raises(ValueError):
        
        @namedtuple(verbose=True, rename=False)
        class Person:
            _fields = 'name 1'


# Plain Function Decorator ########################################################

def test_plain_function_decorator():

    with should_have_verbose_output(False):

        @namedtuple
        def Person(name, age):
            pass

        verify(Person)


# Class Function Factory ######################################################

@pytest.mark.parametrize("verbose", [True, False])
def test_plain_function_decorator_kwargs(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose=verbose)
        def Person(name, age):
            pass

        verify(Person)


@pytest.mark.parametrize("verbose", [True, False])
def test_function_decorator_args(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose, True)
        def Person():
            return 'name 1'

        verify(Person, '_1')


@pytest.mark.parametrize("verbose", [True, False])
def test_function_decorator_args_kwargs(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose, rename=True)
        def Person():
            return 'name 1'

        verify(Person, '_1')


@pytest.mark.parametrize("verbose", [True, False])
def test_function_decorator_kwargs_2(verbose):

    with should_have_verbose_output(verbose):

        @namedtuple(verbose=verbose, rename=True)
        def Person():
            return 'name 1'

        verify(Person, '_1')


# Class Function Should Raise #################################################

def test_function_decorator_should_raise():

    with pytest.raises(ValueError):

        @namedtuple
        def Person():
            return 'name 1'


def test_function_decorator_kwargs_should_raise():

    with pytest.raises(ValueError):

        @namedtuple(verbose=True)
        def Person():
            return 'name 1'


def test_function_decorator_args_should_raise():

    with pytest.raises(ValueError):

        @namedtuple(True, False)
        def Person():
            return 'name 1'


def test_function_decorator_args_kwargs_should_raise():

    with pytest.raises(ValueError):

        @namedtuple(True, rename=False)
        def Person():
            return 'name 1'


def test_function_decorator_kwargs_2_should_raise():

    with pytest.raises(ValueError):

        @namedtuple(verbose=True, rename=False)
        def Person():
            return 'name 1'


# Used like std ################################################################

@pytest.mark.parametrize("verbose", [True, False])
def test_used_like_std(verbose):

    # TODO : Split this into smaller test functions

    with should_have_verbose_output(False):
        Person = namedtuple('Person', 'name age')
        verify(Person)

    with should_have_verbose_output(verbose):
        Person = namedtuple('Person', 'name age', verbose)
        verify(Person)

    with should_have_verbose_output(False):
        Person = namedtuple('Person', 'name 1', rename=True)
        verify(Person, '_1')

    with should_have_verbose_output(verbose):
        Person = namedtuple('Person', 'name age', verbose=verbose)
        verify(Person)

    with should_have_verbose_output(verbose):
        Person = namedtuple('Person', 'name 1', verbose, True)
        verify(Person, '_1')

    with should_have_verbose_output(verbose):
        Person = namedtuple('Person', 'name 1', verbose, rename=True)
        verify(Person, '_1')

    with should_have_verbose_output(verbose):
        Person = namedtuple('Person', 'name 1', verbose=verbose, rename=True)
        verify(Person, '_1')

    with should_have_verbose_output(False):
        Person = namedtuple('Person', field_names='name age')
        verify(Person)

    with should_have_verbose_output(False):
        Person = namedtuple('Person', field_names='name 1', rename=True)
        verify(Person, '_1')

    with should_have_verbose_output(verbose):
        Person = namedtuple('Person', field_names='name age', verbose=verbose)
        verify(Person)

    with should_have_verbose_output(verbose):
        Person = namedtuple('Person', field_names='name 1', verbose=verbose, rename=True)
        verify(Person, '_1')

    with should_have_verbose_output(False):
        Person = namedtuple(typename='Person', field_names='name age')
        verify(Person)

    with should_have_verbose_output(False):
        Person = namedtuple(typename='Person', field_names='name 1', rename=True)
        verify(Person, '_1')

    with should_have_verbose_output(verbose):
        Person = namedtuple(typename='Person', field_names='name age', verbose=verbose)
        verify(Person)

    with should_have_verbose_output(verbose):
        Person = namedtuple(typename='Person', field_names='name 1', verbose=verbose, rename=True)
        verify(Person, '_1')


# Used like std (should raise) #################################################

@pytest.mark.parametrize("args", [
    dict(args=('Person', 'name 1',), kwargs=dict()),
    dict(args=('Person', 'name 1', True,), kwargs=dict()),
    dict(args=('Person', 'name 1',), kwargs=dict(verbose=True)),
    dict(args=('Person',), kwargs=dict(field_names='name 1')),
    dict(args=('Person',), kwargs=dict(field_names='name 1', verbose=True)),
    dict(args=(), kwargs=dict(typename='Person', field_names='name 1')),
    dict(args=(), kwargs=dict(typename='Person',field_names='name 1',
                              verbose=True)),
])
def test_used_like_std_should_raise(args):
    """
    Verify that an exception is raised when an invalid field name is present,
    and rename == False.
    """
    with pytest.raises(ValueError):
        namedtuple(*args['args'], **args['kwargs'])


# Decorator with docstring #####################################################

def test_decorator_with_docstring():

    @namedtuple
    class Person:
        """
        A named tuple.
        """
        _fields = 'name age'

    doc_expected = """
        A named tuple.
        """

    verify(Person, doc_expected=doc_expected)