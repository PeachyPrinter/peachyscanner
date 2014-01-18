import cv2

class PeachyScanner(object):
    def run(self):
        print("Starting Up")


class Mapper(object):
    debug = False
    def info(self,val):
        if (self.debug):
            print(val)

    def __init__(self,bgr_colour,threshold):
        self.b_match,self.g_match, self.r_match = bgr_colour
        self.set_threshold(threshold)

    def set_threshold(self, threshold):
        self.threshold = threshold

    def set_colour(self, bgr_colour):
        self.b_match,self.g_match, self.r_match = bgr_colour

    def _get_lower(self, value):
        lower = value - self.threshold
        if lower < 0:
            lower = 0
        return lower

    def _get_upper(self, value):
        upper = value + self.threshold
        if upper > 255:
            upper = 255
        return upper

    def get_threshold_array(self,img):
        b,g,r = cv2.split(img)
        bc = cv2.inRange(b,self._get_lower(self.b_match), self._get_upper(self.b_match))
        gc = cv2.inRange(g,self._get_lower(self.g_match), self._get_upper(self.g_match))
        rc = cv2.inRange(r,self._get_lower(self.r_match), self._get_upper(self.r_match))
        bg = cv2.bitwise_and(bc,gc)
        bgr = cv2.bitwise_and(bg,rc)
        return bgr

    def _get_first_point(self, array):
        for index in range(len(array)):
            if array[index] == 255:
                return index
        return -1

    def _get_first_points(self, img):
        array = self.get_threshold_array(img)
        return [ self._get_first_point(array[row]) for row in range(img.shape[0]) ]
        

    def get_points(self,img):
        self.info('MATCH R: %d G: %d B: %d' % (self.r_match,self.g_match, self.b_match))
        return self._get_first_points(img)

if __name__ == "__main__":
    PeachyScanner().run()