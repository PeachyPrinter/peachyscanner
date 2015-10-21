

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

    def __init__(self, frame_size, frame_column):
        self._image = np.zeros((frame_size.shape[0], frame_size.shape[1], 3)

    def process(self, frame, frame_count):
        self._image[frame_count] = frame[frame_column]
        self.status.update_image(self._image)

    def save(self):
        pass

class God(object):

    def __init__(self):
        encoder
        detectors
        # image_capture
        # point_capture

    def start()
        ImageCapture(frame_size, image_data_location)

    def process(frame):
        until done:
            process stuff



class FrameDisplatcher:
    def subscribe
    def unsubscribe

    def process(frame_event)


class Frame()
    self._image

class FrameWithRegeonOfInterest

class EdgePosisitionFrame()
    def __init__(self, detector):
        return self

    def __call__(self, frame):
        self.mask = detector.calculate_mask(self.frame)

class RecordFrameData()
    def __init__(self, frame):
        return self











