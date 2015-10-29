import logging

logger = logging.getLogger('peachy')


class ROI(object):
    def __init__(self, x_rel, y_rel, w_rel, h_rel):
        self.x_rel = x_rel
        self.y_rel = y_rel
        self.w_rel = w_rel
        self.h_rel = h_rel
        self.center_line = 0.5
        if self.center_line > (self.x_rel + self.w_rel) or self.center_line < self.x_rel:
            raise Exception('Region of interest must span the center of frame: {}->{}'.format(self.x_rel, self.w_rel))

    @classmethod
    def set_from_abs_points(cls, point1, point2, frame_shape):
        x_abs = min(point1[0], point2[0])
        y_abs = min(point1[1], point2[1])
        w_abs = abs(point1[0] - point2[0])
        h_abs = abs(point1[1] - point2[1])

        logger.info('ABS ROI {} {} {} {} FRAME {} {}'.format(x_abs, y_abs, w_abs, h_abs, frame_shape[0], frame_shape[1]))

        x_rel = x_abs / float(frame_shape[1])
        y_rel = y_abs / float(frame_shape[0])
        w_rel = w_abs / float(frame_shape[1])
        h_rel = h_abs / float(frame_shape[0])

        logger.info('REL ROI {} {} {} {}'.format(x_rel, y_rel, w_rel, h_rel))

        return ROI(x_rel, y_rel, w_rel, h_rel)

    def overlay(self, frame, amount=0.5):
        gray = frame / int(1 / amount)
        roi = self.get(frame)
        return self.replace(gray, roi)

    def replace(self, full_frame, new_part):
        x_abs, y_abs, w_abs, h_abs = self._get_absolute(full_frame.shape)
        full_frame[y_abs:y_abs + new_part.shape[0], x_abs:x_abs + new_part.shape[1]] = new_part
        return full_frame

    def _get_absolute(self, shape):
        x_abs = shape[1] * self.x_rel
        y_abs = shape[0] * self.y_rel
        w_abs = shape[1] * self.w_rel
        h_abs = shape[0] * self.h_rel
        return (x_abs, y_abs, w_abs, h_abs)

    def get(self, frame):
        x_abs, y_abs, w_abs, h_abs = self._get_absolute(frame.shape)
        return frame[y_abs:y_abs + h_abs, x_abs:x_abs + w_abs]

    def copy(self):
        return ROI(self.x_rel, self.y_rel, self.w_rel, self.h_rel)

    def get_left_of_center(self, frame):
        x_abs, y_abs, w_abs, h_abs = self._get_absolute(frame.shape)
        center = frame.shape[1] / 2
        return frame[y_abs:y_abs + h_abs, x_abs:center]

    def get_points(self):
        return [self.x_rel, self.y_rel, self.w_rel, self.h_rel]
