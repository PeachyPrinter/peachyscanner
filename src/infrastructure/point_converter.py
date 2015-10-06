import numpy as np


class PointConverter(object):
    def __init__(self):
        pass

    def get_points(self, frame, center):
        # print('GP in  {}'.format(frame.shape))
        roi = frame
        # print('GP roi {}'.format(roi.shape))
        maxindex = np.argmax(roi, axis=1)
        # print('GP max {}'.format(maxindex.shape))
        result =  (np.ones(maxindex.shape[0]) * center) - maxindex
        # print('GP out {}'.format(result.shape))
        return result
