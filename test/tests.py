import unittest
import sys, os
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import peachyscanner

class PeachyScannerTest(unittest.TestCase):
	def test_peachy(self):
		self.assertEquals(1,1)

class Mapper(unittest.TestCase):
	def test_given_an_image_point_map_returned(self):
		img = cv2.imread('TestData/SimpleTestImage1.jpg',1)
		expected = [0,1,2,3,4,5,6,7,8,9]
		colour = [255,255,255]
		mapper = Mapper(colour)
		actual = mapper.get_points(img) 
		self.assertEquals(expected,actual)


unittest.main()