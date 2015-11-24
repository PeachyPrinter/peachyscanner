import cv2
import os
import numpy as np
import time
from scipy import ndimage


class LaserDetector2(object):
    def __init__(self, threshold=225, filter_size_yx=(3, 3), color='red'):
        self.color = color
        self.threshold = 225
        self._structure = np.ones(filter_size_yx)

    def detect(self, frame):
        channel = cv2.split(frame)[2]
        ranged_image = cv2.inRange(channel, self.threshold, 255)
        noise_reduction = ndimage.binary_erosion(ranged_image, structure=self._structure).astype(ranged_image.dtype) * 255
        return noise_reduction


sld  = LaserDetector2()

try:
    local = os.path.dirname(os.path.realpath(__file__))
    image_path = os.path.join(local, 'test_image.jpg')
    print(image_path)
    source_image = cv2.imread(image_path)
    cap = cv2.VideoCapture(0)
    ret, source_image = cap.read()
    if source_image is not None:
        while True:
            ret, source_image = cap.read()
            start = time.time()
            mask = sld.detect(source_image)
            total = time.time() - start
            print("Time ms : {}".format(str(total * 100)))
            cv2.imshow('source', source_image)
            cv2.imshow('frame', mask)
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == 'q':
                break
            if key == '+':
                sld.low += 1
            if key =='-':
                sld.low -= 1
            if key == '9':
                sld.structure = np.ones((sld.structure.shape[0] + 1, sld.structure.shape[1] + 1))
            if key == '6':
                sld.structure = np.ones((max(1, sld.structure.shape[0] - 1), max(1, sld.structure.shape[1] - 1)))
            # if key == '8':
            #     sld.region_y += 2
            # if key == '5':
            #     sld.region_y = max(3, sld.region_y - 2)
            # print "LOW: {} shape: {}".format(sld.low, str(sld.structure.shape))
finally:
    cv2.destroyAllWindows()
    cap.release()