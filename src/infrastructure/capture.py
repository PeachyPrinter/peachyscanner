

class PointCapture(object):
    def __init__(self, status, detector, encoder):
        pass

    def process(self, frame, roi):
        pass

    def start(self, complete_callback):
        pass

    def save(self):
        pass


class ImageCapture(object):

    def __init__(self, status, encoder):
        pass

    def process(self, frame, roi):
        pass

    def start(self, complete_callback):
        pass

    def save(self):
        pass