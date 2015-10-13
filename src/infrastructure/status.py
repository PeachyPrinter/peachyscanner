

class Status(object):
    def __init__(self):
       self._operation = "Startup"
       self._progress = 1.0
       self._handlers = []

    @property
    def operation(self):
        return self._operation

    @operation.setter
    def operation(self, value):
        self._operation = value
        self._update()
        return self._operation

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self._update()
        return self._progress

    def _update(self):
        for handler in self._handlers:
            handler(self)

    def register_handler(self, handler):
        self._handlers.append(handler)