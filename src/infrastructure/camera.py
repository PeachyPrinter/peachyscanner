import cv2
from cv2 import VideoCapture
import logging

logger = logging.getLogger('peachy')

global_camera_properties = [
{'name': 'Brightness',      'value': cv2.CAP_PROP_BRIGHTNESS},
{'name': 'Contrast',        'value': cv2.CAP_PROP_CONTRAST},
{'name': 'Saturation',      'value': cv2.CAP_PROP_SATURATION},
{'name': 'Hue',             'value': cv2.CAP_PROP_HUE},
{'name': 'Gain',            'value': cv2.CAP_PROP_GAIN},
{'name': 'Exposure',        'value': cv2.CAP_PROP_EXPOSURE},
]


class Camera(object):

    def __init__(self, focal_length_mm, sensor_size_xy_mm):
        assert(len(sensor_size_xy_mm) == 2)
        self.focal_length_mm = focal_length_mm
        self.sensor_size_xy_mm = sensor_size_xy_mm

    def get_settings(self):
        if not hasattr(self, '_video_capture'):
            raise Exception("Start video capture before getting settings")
        settings = []
        for prop in global_camera_properties:
            prop_value = self._video_capture.get(prop['value'])
            if prop_value >= 0:
                settings.append({'name': prop['name'], 'value': prop_value})
        return settings

    def set_setting(self, setting, value):
        if not hasattr(self, '_video_capture'):
            raise Exception("Start video capture before setting a setting")
        setting_id = filter(lambda x: x['name'] == setting, global_camera_properties)
        if len(setting_id) == 1:
            setting_id = setting_id[0]['value']
        else:
            raise Exception("Setting {} not available".format(setting))
        self._video_capture.set(setting_id, value)

    def read(self):
        (retVal, image) = self._video_capture.read()
        return image

    def start(self):
        self._video_capture = VideoCapture(0)
        self.shape = self.read().shape

    def stop(self):
        self._video_capture.release()
