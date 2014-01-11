import cv2

class PeachyScanner(object):
	def run(self):
		print("Starting Up")


class Mapper(object):
	debug = False
	def info(self,val):
		if (self.debug):
			print(val)

	def __init__(self,colour,threshold):
		self.b_match,self.g_match, self.r_match = colour
		self.set_threshold(threshold)

	def set_threshold(self, threshold):
		self.b_threshold, self.g_threshold, self.r_threshold = threshold

	def _get_first_match(self, ypos, width, img):
		for xpos in range(0,width):
			b_px = img.item(ypos,xpos,0)
			g_px = img.item(ypos,xpos,1)
			r_px = img.item(ypos,xpos,2)
			self.info('R: %d G: %d B: %d' % (r_px, g_px, b_px))
			if (
				abs(self.r_match - r_px) <= self.r_threshold and
				abs(self.g_match - g_px) <= self.g_threshold and
				abs(self.b_match - b_px) <= self.b_threshold
				):
					return xpos
		return -1

	def get_points(self,img):
		height = img.shape[0]
		width = img.shape[1]

		self.info("Image Height: %d" % height)
		self.info("Image Width: %d" % width)
		self.info('MATCH R: %d G: %d B: %d' % (self.r_match,self.g_match, self.b_match))
		self.info('Threshold R: %d G: %d B: %d' % (self.r_threshold, self.g_threshold, self.b_threshold))

		
		return [ self._get_first_match(ypos, width, img) for ypos in range(0,height) ] 

if __name__ == "__main__":
	PeachyScanner().run()