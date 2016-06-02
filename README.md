# namedtuple_decorator

A drop in replacement for the standard namedtuple that supports use as a class and function decorator:

```python
@namedtuple
class Point:
    '''an element of some set called a space'''
    _fields = 'x y'
```

```python
@namedtuple
def Point:
    '''an element of some set called a space'''
    return 'x y'
```