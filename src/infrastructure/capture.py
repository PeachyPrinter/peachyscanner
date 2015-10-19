

# class PointCapture(object):
#     def __init__(self, status, detector, encoder):
#         pass

#     def process(self, frame):
#         pass

#     def start(self, complete_callback):
#         pass

#     def save(self):
#         pass


class ImageCapture(object):

    def __init__(self, status, frame_size, frame_column):
        self._image = np.zeros((frame_size.shape[0], frame_size.shape[1], 3)
        pass

    def process(self, frame, frame_count):
        self._image[frame_count] = frame[frame_column]
        self.status.update_image(self._image)

    def save(self):
        pass