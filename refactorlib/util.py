"""
Miscellany utilities for refactorlib.

I reserve the right to move these to another namespace in the future.
"""
from subprocess import Popen as _Popen, PIPE, CalledProcessError
PIPE = PIPE  ## hush, lint.

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

def which(cmd):
    """
    Use unix which(1) to find a command.
    Return a string path to the command on success.
    Return None on failure.
    """
    from subprocess import Popen, PIPE
    p = Popen(('/usr/bin/which', 'node'), stdout=PIPE)
    stdout, _ = p.communicate()
    if p.returncode == 0:
        return stdout.strip()
    else:
        return None

def static(**kwargs):
    def decorator(func):
        for attr, val in kwargs.items():
            setattr(func, attr, val)
        return func
    return decorator

class Popen(_Popen):
    """Add a check_output method to Popen."""
    def __init__(self, args, *more_args, **kwargs):
        super(Popen, self).__init__(args, *more_args, **kwargs)
        self.args = args

    def check_output(self, input=None):
        r"""Run command with arguments and return its output as a byte string.

        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.
        """
        output, _ = self.communicate(input)
        retcode = self.poll()
        if retcode:
            cmd = self.args
            raise CalledProcessError(retcode, cmd)
        return output
