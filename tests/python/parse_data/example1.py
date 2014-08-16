
# This is an import
from mylib import (
        mydecorator1, mydecorator2
)

# Here are two decorators
@mydecorator1
@mydecorator2
def myfunc(myarg="mystring"):
    "This is a docstring for myfunc"
    myvar = myarg.upper()
    return myvar

# Here's a trailing comment

