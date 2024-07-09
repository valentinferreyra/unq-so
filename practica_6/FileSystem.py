class FileSystem():
    def __init__(self):
        self._files = {}

    def write(self, path, data):
        self._files[path] = data

    def read(self, path):
        return self._files[path]