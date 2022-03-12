from cached_property import cached_property


class FileType:
    def __init__(self, filetype, suffixes):
        self.name = filetype
        if hasattr('__iter__', suffixes):
            self.suffixes = suffixes
        else:
            # Make it into a one-item tuple
            self.suffixes = (suffixes,)

    def match(self, filename):
        for suffix in self.suffixes:
            if filename.endswith('.' + suffix):
                return True
        else:
            return False

    @cached_property
    def parser(self):
        module = __import__('refactorlib.%s.parse' % self.name, fromlist=[None])
        return getattr(module, 'parse')

    @cached_property
    def encoding_detector(self):
        module = __import__('refactorlib.%s.parse' % self.name, fromlist=[None])
        return getattr(module, 'detect_encoding', lambda filename: None)


class FileTypes:
    """
    A collection of FileType's
    """

    def __init__(self):
        self.filetypes = {}

    def register(self, *args, **kwargs):
        self.register_filetype(FileType(*args, **kwargs))

    def register_filetype(self, filetype):
        self.filetypes[filetype.name] = filetype

    def detect_filetype(self, filename, filetype=None):
        if filetype:
            return self.get_filetype(filetype).parser

        for filetype in self.filetypes.values():
            if filetype.match(filename):
                return filetype
        else:
            raise ValueError('Unsupported file type: %r' % filename)

    def get_filetype(self, filetype):
        try:
            return self.filetypes[filetype]
        except KeyError:
            raise ValueError('Unsupported file type: %r' % filetype)


FILETYPES = FileTypes()
FILETYPES.register('cheetah', 'tmpl')
FILETYPES.register('python', 'py')
FILETYPES.register('javascript', 'js')

__all__ = ('FILETYPES',)
