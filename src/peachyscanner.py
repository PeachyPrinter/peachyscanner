import cv2

class PeachyScanner(object):
	def run(self):
		print("Starting Up")


class Mapper(object):
	def __init__(self,colour):
		self.colour = colour

	def _get_first_match(self, ypos, width, img):
		for xpos in range(0,width):
			r,g,b = img[xpos,ypos]
			if ([r,g,b] == self.colour):
				return xpos
		return -1

	def get_points(self,img):
		height = img.shape[0]
		width = img.shape[1]
		return [ self._get_first_match(ypos, width, img) for ypos in range(0,height) ] 

if __name__ == "__main__":
	PeachyScanner().run()