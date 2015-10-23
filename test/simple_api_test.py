import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.scanner import ScannerAPI
import cv2


class Goer(object):
    def __init__(self):
        self.api = ScannerAPI()
        self.image = None
        self.api.capture_image(self.callback)

    def callback(self, image):
        self.image = image.image

    def run(self):
        try:
            self.api.start()
            key = 'a'
            while(key != 'q'):
                if self.image is not None:
                    print('running')
                    cv2.imshow('frame', self.image)
                    key = chr(cv2.waitKey(1) & 0xFF)
        finally:
            cv2.destroyAllWindows()
            self.api.stop()

if __name__ == '__main__':
    Goer().run()
