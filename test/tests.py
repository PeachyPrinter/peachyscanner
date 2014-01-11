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
        threshold = [0,0,0]
        mapper = Mapper(colour,threshold)
        actual = mapper.get_points(img)
        self.assertEquals(expected,actual)

    def test_given_an_image_with_non_complete_points_a_point_map_returned(self):
        img = cv2.imread('TestData/SimpleTestImage4.png',1)
        expected = [-1,-1] + [i for i in range(2,9)] + [-1,-1] + [i for i in range(11,18)] + [-1,-1]
        colour = [255,255,255]
        threshold = [0,0,0]
        mapper = Mapper(colour,threshold)
        actual = mapper.get_points(img)
        self.assertEquals(expected,actual)

    def test_given_an_image_with_no_points_a_point_map_returned(self):
        img = cv2.imread('TestData/SimpleTestImage5.png',1)
        expected = [-1 for i in range(0,20)]
        colour = [255,255,255]
        threshold = [0,0,0]
        mapper = Mapper(colour,threshold)
        actual = mapper.get_points(img)
        self.assertEquals(expected,actual)

    def test_given_an_colour_image_and_specific_colour_a_point_map_returned(self):
        img = cv2.imread('TestData/SimpleTestImage2.png',1)
        expected = [i for i in range(0,20)]
        colour = [255,128,0]
        threshold = [0,0,0]
        mapper = Mapper(colour,threshold)
        actual = mapper.get_points(img)
        self.assertEquals(expected,actual)

    def test_given_a_threshold_items_in_threshold_work_for_red(self):
        img = cv2.imread('TestData/RedThresholdTest.png',1)
        threshold = [0,0,20]
        expected = [0,0,0,-1,-1] 
        colour = [128,128,128]
        mapper = Mapper(colour, threshold)
        actual = mapper.get_points(img)
        self.assertEquals(expected,actual)

    def test_given_a_threshold_items_in_threshold_work_for_green(self):
        img = cv2.imread('TestData/GreenThresholdTest.png',1)
        threshold = [0,20,0]
        expected = [0,0,0,-1,-1] 
        colour = [128,128,128]
        mapper = Mapper(colour, threshold)
        actual = mapper.get_points(img)
        self.assertEquals(expected,actual)

    def test_given_a_threshold_items_in_threshold_work_for_blue(self):
        img = cv2.imread('TestData/BlueThresholdTest.png',1)
        threshold = [20,0,0]
        expected = [0,0,0,-1,-1] 
        colour = [128,128,128]
        mapper = Mapper(colour, threshold)
        actual = mapper.get_points(img)
        self.assertEquals(expected,actual)



unittest.main()