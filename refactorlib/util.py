"""
Miscellany utilities for refactorlib.

I reserve the right to move these to another namespace in the future.
"""

class LazyProperty(object):
    """
    A decorator for a property which only needs calculated once.
    """
    def __init__(self, calculate_function):
        self._calculate = calculate_function
    
    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._calculate(obj)
        setattr(obj, self._calculate.func_name, value)
        return value
