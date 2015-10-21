
class ImageCapture():
    def handle(self, frame=None):
        pass

class PointsCapture():
    def __init__(self, shape):
        array

    def handle(self, mask=None):
        data = self.get_points(mask)
        pop array
        if array is full
        return 0

    def get_points(self, frame):
        maxindex = np.argmax(frame, axis=1)
        data = (np.ones(maxindex.shape[0]) * maxindex.shape[0]) - maxindex
        data[data < 0] = 0
        data[data == maxindex.shape[0]] = 0
        return data