import unittest
import sys, os
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from peachyscanner import Mapper

class PeachyScannerTest(unittest.TestCase):
	def test_peachy(self):
		self.assertEquals(1,1)

class MapperTest(unittest.TestCase):
	def test_given_an_image_point_map_returned(self):
		img = cv2.imread('TestData/SimpleTestImage1.png',1)
		expected = [i for i in range(0,20)]
		colour = [255,255,255]
		mapper = Mapper(colour)
		actual = mapper.get_points(img)
		self.assertEquals(expected,actual)

	def test_given_an_colour_image_point_map_returned(self):
		img = cv2.imread('TestData/SimpleTestImage2.png',1)
		expected = [i for i in range(0,20)]
		colour = [255,128,0]
		mapper = Mapper(colour)
		actual = mapper.get_points(img)
		self.assertEquals(expected,actual)

	# def test_given_an_variable_colour_image_point_map_returned(self):
	# 	img = cv2.imread('TestData/SimpleTestImage3.png',1)
	# 	expected = [i for i in range(0,20)]
	# 	colour = [255,128,0]
	# 	mapper = Mapper(colour)
	# 	actual = mapper.get_points(img)
	# 	self.assertEquals(expected,actual)

unittest.main()