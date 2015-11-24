import cv2
import os
import numpy as np
import time
from numpy.lib.stride_tricks import as_strided

class ImageFiltering(object):
    def chunk_view(self, image, chunk):
        shape = (image.shape[0] - chunk[0] + 1, image.shape[1] - chunk[1] + 1) + chunk + (image.shape[2],)
        strides = (image.strides[0], image.strides[1]) + image.strides
        return as_strided(image, shape=shape, strides=strides)

    def averages(self, block):
        left = np.mean(block, axis=2,)
        up = np.mean(left, axis=2,)
        return up

class SpikeLaserDetector(ImageFiltering):
    def __init__(self, low_bgr, high_bgr):
        for idx in range(3):
            if low_bgr[idx] > high_bgr[idx]:
                raise Exception('Low range exceeds high range {} !< {}'.format(str(low_bgr), str(high_bgr)))
        self.low = 15
        self.low_bgr = low_bgr
        self.high_bgr = high_bgr
        self.region_x = 3
        self.region_y = 15

    @classmethod
    def from_rgb_float(cls, low_rgb, high_rgb):
        low = (int(low_rgb[2] * 255), int(low_rgb[1] * 255), int(low_rgb[0] * 255))
        high = (int(high_rgb[2] * 255), int(high_rgb[1] * 255), int(high_rgb[0] * 255))
        return cls(low, high)

    def detect(self, frame):
        region_shape = (self.region_x, self.region_y)
        a = self.chunk_view(frame, region_shape)
        b = self.averages(a)
        border = (region_shape[0] / 2, region_shape[1] / 2)
        c = frame[border[0]:-border[0], border[1]:-border[1]] - b

        lum = np.average(b, axis=2)
        r, g, b = cv2.split(c)

        e = cv2.inRange(r - lum, self.low, 255)
        return e


sld  = SpikeLaserDetector((235, 235, 235), (255, 255, 255))

try:
    local = os.path.dirname(os.path.realpath(__file__))
    image_path = os.path.join(local, 'test_image.jpg')
    print(image_path)
    source_image = cv2.imread(image_path)
    # cap = cv2.VideoCapture(0)
    # ret, source_image = cap.read()
    if source_image is not None:
        while True:
            # ret, source_image = cap.read()
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
                sld.region_x += 2
            if key == '6':
                sld.region_x = max(3, sld.region_x - 2)
            if key == '8':
                sld.region_y += 2
            if key == '5':
                sld.region_y = max(3, sld.region_y - 2)
            print ('Low: {} Region: {},{}'.format(sld.low, sld.region_x, sld.region_y))
finally:
    cv2.destroyAllWindows()
    cap.release()