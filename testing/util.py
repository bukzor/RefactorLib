"""
A home for the 'yellow code' of testing.
"""
from os.path import join


FAILURE_SUFFIX = '.test_failure'


def example_dir(func):
    from os.path import relpath

    modulefile = __import__(func.__module__, fromlist=True).__file__
    dirname = modulefile.rsplit('_test', 1)[0] + '_data'
    return relpath(dirname)


def get_examples(func):

    from os import listdir
    from os.path import isfile

    examples = example_dir(func)
    examples_found = False

    for example in listdir(examples):
        if example.startswith('.'):
            # Hidden file.
            continue
        elif example.endswith(FAILURE_SUFFIX):
            # Left over from previous test failure.
            continue

        example = join(examples, example)
        if isfile(example):
            yield example,
            examples_found = True

    if not examples_found:
        raise SystemError("No examples found in %r" % examples)


def get_output(suffix=None, func=None):
    def _get_output(_func):
        if func is not None:
            _func = func

        from os.path import split
        for example, in get_examples(_func):

            dirname, filename = split(example)
            output = join(dirname, _func.__name__, filename)
            if suffix:  # Replace the suffix.
                output = output.rsplit('.', 1)[0] + '.' + suffix

            yield example, output

    # The silly optionally-called decorator pattern.
    if callable(suffix):
        func, suffix = suffix, None
        return _get_output(func)
    else:
        return _get_output


def parametrize(arg_finder):
    def decorator(func):
        arglist = arg_finder(func)
        arglist = tuple(arglist)  # freeze any generators

        import pytest
        from inspect import getargspec
        return pytest.mark.parametrize(getargspec(func).args, arglist)(func)
    return decorator


def assert_same_content(old_file, new_content, extra_suffix=''):
    new_file = ''.join((old_file, extra_suffix, FAILURE_SUFFIX))
    try:
        open(new_file, 'w').write(new_content)
    except IOError as e:
        if e.errno == 2:  # No such file.
            from os import makedirs
            from os.path import dirname
            makedirs(dirname(new_file))
            open(new_file, 'w').write(new_content)
        else:
            raise

    assert_same_file_content(old_file, new_file)


def assert_same_file_content(old_file, new_file):
    old_content = open(old_file).readlines()
    new_content = open(new_file).readlines()

    diffs = diff(old_content, new_content)

    if diffs:
        diffs = 'Results differ:\n--- %s\n+++ %s\n%s' % (old_file, new_file, diffs)
        # py.test derps on non-utf8 bytes, so I force unicode like so:
        diffs = diffs.decode('UTF-8', 'replace')
        raise AssertionError(diffs)
    else:
        from os import unlink
        unlink(new_file)


def diff(old_content, new_content, n=3):
    """similar to difflib.ndiff, but supports limited context lines"""
    from difflib import ndiff as diff
    diffdata = tuple(diff(old_content, new_content))
    difflines = set()
    for lineno, line in enumerate(diffdata):
        if not line.startswith('  '):  # Ignore the similar lines.
            difflines.update(range(lineno - n, lineno + n + 1))

    return '\n'.join(
        line.rstrip('\n')
        for lineno, line in enumerate(diffdata)
        if lineno in difflines
    )
