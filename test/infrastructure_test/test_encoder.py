import unittest
import sys
import os
import numpy as np
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.encoder import Encoder

class EncoderTest(unittest.TestCase):
    def test_degrees_starts_at_0(self):
        encoder = Encoder()
        self.assertEqual(0.0, encoder.degrees)

    def test_process_given_alternating_BW_adds_expected_degrees(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage = np.ones((100,100,3),dtype='uint8') * 255
        expected_degrees = 4.0
        encoder = Encoder()

        for image in [whiteimage, blackimage, whiteimage,blackimage, ]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)

    def test_degress_increments_set_amount(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage = np.ones((100,100,3),dtype='uint8') * 255
        expected_degrees = 8.0
        encoder = Encoder(degrees_per_step=2.0)

        for image in [whiteimage, blackimage, whiteimage,blackimage, ]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)

    def test_encoder_points_increments_set_amount(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage = np.ones((100,100,3),dtype='uint8') * 255
        expected_degrees = 8.0
        encoder = Encoder(encoder_sections=180)

        for image in [whiteimage, blackimage, whiteimage,blackimage, ]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)


    def test_process_given_alternating_BW_adds_expected_degrees_only_on_change(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage = np.ones((100,100,3),dtype='uint8') * 255
        expected_degrees = 2.0
        encoder = Encoder()

        for image in [whiteimage, whiteimage, blackimage, blackimage]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)


    def test_process_given_alternating_BW_adds_expected_degrees_at_specific_point(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage[4][4] = [255,255,255]
        expected_degrees = 4.0
        encoder = Encoder(encoder_point=[4, 4])

        for image in [whiteimage, blackimage, whiteimage,blackimage, ]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)

    def test_encoder_point_sets_encoder_point(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage = np.zeros((100,100,3),dtype='uint8')
        whiteimage[4][4] = [255,255,255]
        expected_degrees = 4.0
        encoder = Encoder(encoder_point=[0, 0])
        encoder.encoder_point = [4, 4]

        for image in [whiteimage, blackimage, whiteimage,blackimage, ]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)

    def test_process_given_alternating_BW_adds_expected_degrees_within_threshold(self):
        blackimage = np.ones((100,100,3),dtype='uint8') * 100
        nullimage = np.ones((100,100,3),dtype='uint8') * 150
        whiteimage = np.ones((100,100,3),dtype='uint8') * 200
        expected_degrees = 4.0
        encoder = Encoder(threshold=450, null_zone=50)

        for image in [whiteimage, nullimage, blackimage, nullimage, nullimage,  whiteimage, nullimage, blackimage, ]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)

    def test_thrshold_changes_threshold(self):
        blackimage = np.ones((100,100,3),dtype='uint8') * 100
        nullimage = np.ones((100,100,3),dtype='uint8') * 150
        whiteimage = np.ones((100,100,3),dtype='uint8') * 200
        expected_degrees = 4.0
        encoder = Encoder(threshold=382, null_zone=382)

        encoder.threshold = 450
        encoder.null_zone = 50

        for image in [whiteimage, nullimage, blackimage, nullimage, nullimage,  whiteimage, nullimage, blackimage, ]:
            encoder.process(image)

        self.assertEqual(expected_degrees, encoder.degrees)

    def test_overlay_places_encoder_indicator_correct_place(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        encoder = Encoder(encoder_point=[50, 50])
        encoder.process(blackimage)
        resulting_image = encoder.overlay_encoder(blackimage)
        #Encode indicator is a circle centered on point with some decoration, just checking for one point
        self.assertTrue((resulting_image[52][52] == [0, 0, 255]).all())

    def test_overlay_encoder_places_encoder_indicator_correct_place_if_wont_fit(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        encoder = Encoder(encoder_point=[2, 2])
        encoder.process(blackimage)
        resulting_image = encoder.overlay_encoder(blackimage)
        #Encode indicator is a circle centered on point with some decoration, just checking for one point
        self.assertTrue((resulting_image[4][4] == [0, 0, 255]).all())

    def test_overlay_encoder_indicator_color_is_correct(self):
        blackimage = np.zeros((100,100,3),dtype='uint8')
        greyimage = np.ones((100,100,3),dtype='uint8') * 128
        whiteimage = np.ones((100,100,3),dtype='uint8') * 255
        encoder = Encoder(encoder_point=[50, 50],threshold=384, null_zone=50)
        encoder.process(blackimage)
        resulting_image = encoder.overlay_encoder(blackimage)
        self.assertTrue((resulting_image[52][52] == [0, 0, 255]).all())
        encoder.process(greyimage)
        resulting_image = encoder.overlay_encoder(blackimage)
        self.assertTrue((resulting_image[52][52] == [0, 255, 255]).all())
        encoder.process(whiteimage)
        resulting_image = encoder.overlay_encoder(blackimage)
        self.assertTrue((resulting_image[52][52] == [0, 255, 0]).all())

    def test_overlay_history_shows_threshold_and_null_lines(self):
        image = np.ones((255,255,3),dtype='uint8') * 10
        encoder = Encoder(encoder_point=[50, 50],threshold=300, null_zone=150)
        encoder.process(image)
        resulting_image = encoder.overlay_history(image)
        self.assertTrue((resulting_image[150][9] == [255,255,255]).all())
        self.assertTrue((resulting_image[50][9] == [255,255,255]).all())


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()