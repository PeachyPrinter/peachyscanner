import kivy
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.properties import BoundedNumericProperty
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock

import numpy as np
import threading
from infrastructure.hardware import HardwareConfiguration

kivy.require('1.9.0')
Builder.load_file('ui/hardware.kv')


class HardwareConfig(Popup):
    camera_focal_length_mm = BoundedNumericProperty(10.0, min=0.01, max=100.0)
    sensor_size_x_mm = BoundedNumericProperty(10.0, min=0.01, max=100)
    sensor_size_y_mm = BoundedNumericProperty(7.5, min=0.01, max=100)
    focal_point_to_center = BoundedNumericProperty(100.0, min=0.01, max=10000.0)
    laser_intersection_degree_1 = BoundedNumericProperty(35.0, min=0.0, max=90.0)
    laser_intersection_degree_2 = BoundedNumericProperty(40.0, min=0.0, max=90.0)
    laser_intersection_degree_3 = BoundedNumericProperty(45.0, min=0.0, max=90.0)
    laser_intersection_degree_4 = BoundedNumericProperty(50.0, min=0.0, max=90.0)
    laser_intersection_degree_5 = BoundedNumericProperty(55.0, min=0.0, max=90.0)
    laser_intersection_distance_1 = BoundedNumericProperty(249.9, min=0.0, max=10000.0)
    laser_intersection_distance_2 = BoundedNumericProperty(208.9, min=0.0, max=10000.0)
    laser_intersection_distance_3 = BoundedNumericProperty(175.0, min=0.0, max=10000.0)
    laser_intersection_distance_4 = BoundedNumericProperty(146.8, min=0.0, max=10000.0)
    laser_intersection_distance_5 = BoundedNumericProperty(122.5, min=0.0, max=10000.0)


    def __init__(self, scanner, **kwargs):
        self.section = 'peachyscanner.hardware'
        self.scanner = scanner
        Config.adddefaultsection(self.section)
        super(HardwareConfig, self).__init__(**kwargs)
        Clock.schedule_once(self._load)

    def _load(self, *largs):
        self.camera_focal_length_mm = float(Config.getdefault(self.section, 'camera_focal_length_mm', '10.0'))
        self.sensor_size_x_mm = float(Config.getdefault(self.section, 'sensor_size_x_mm', '10.0'))
        self.sensor_size_y_mm = float(Config.getdefault(self.section, 'sensor_size_y_mm', '10.0'))
        self.focal_point_to_center = float(Config.getdefault(self.section, 'focal_point_to_center', '100.0'))
        self.laser_intersection_degree_1 = float(Config.getdefault(self.section, 'laser_intersection_degree_1', '35.0'))
        self.laser_intersection_degree_2 = float(Config.getdefault(self.section, 'laser_intersection_degree_2', '40.0'))
        self.laser_intersection_degree_3 = float(Config.getdefault(self.section, 'laser_intersection_degree_3', '45.0'))
        self.laser_intersection_degree_4 = float(Config.getdefault(self.section, 'laser_intersection_degree_4', '50.0'))
        self.laser_intersection_degree_5 = float(Config.getdefault(self.section, 'laser_intersection_degree_5', '55.0'))
        self.laser_intersection_distance_1 = float(Config.getdefault(self.section, 'laser_intersection_distance_1', '249.9'))
        self.laser_intersection_distance_2 = float(Config.getdefault(self.section, 'laser_intersection_distance_2', '208.9'))
        self.laser_intersection_distance_3 = float(Config.getdefault(self.section, 'laser_intersection_distance_3', '175.0'))
        self.laser_intersection_distance_4 = float(Config.getdefault(self.section, 'laser_intersection_distance_4', '146.8'))
        self.laser_intersection_distance_5 = float(Config.getdefault(self.section, 'laser_intersection_distance_5', '122.5'))

    def _save(self):
        Config.set(self.section, 'camera_focal_length_mm', str(self.camera_focal_length_mm))
        Config.set(self.section, 'sensor_size_x_mm', str(self.sensor_size_x_mm))
        Config.set(self.section, 'sensor_size_y_mm', str(self.sensor_size_y_mm))
        Config.set(self.section, 'focal_point_to_center', str(self.focal_point_to_center))
        Config.set(self.section, 'laser_intersection_degree_1', str(self.laser_intersection_degree_1))
        Config.set(self.section, 'laser_intersection_degree_2', str(self.laser_intersection_degree_2))
        Config.set(self.section, 'laser_intersection_degree_3', str(self.laser_intersection_degree_3))
        Config.set(self.section, 'laser_intersection_degree_4', str(self.laser_intersection_degree_4))
        Config.set(self.section, 'laser_intersection_degree_5', str(self.laser_intersection_degree_5))
        Config.set(self.section, 'laser_intersection_distance_1', str(self.laser_intersection_distance_1))
        Config.set(self.section, 'laser_intersection_distance_2', str(self.laser_intersection_distance_2))
        Config.set(self.section, 'laser_intersection_distance_3', str(self.laser_intersection_distance_3))
        Config.set(self.section, 'laser_intersection_distance_4', str(self.laser_intersection_distance_4))
        Config.set(self.section, 'laser_intersection_distance_5', str(self.laser_intersection_distance_5))
        Config.write()

    def deg_to_rad(self, degree):
        float(self.laser_intersection_degree) / 360 * 2 * np.pi

    def hardware(self):
        intersections_rad_mm = [
            (self.deg_to_rad(self.laser_intersection_degree_1), self.laser_intersection_distance_1),
            (self.deg_to_rad(self.laser_intersection_degree_2), self.laser_intersection_distance_2),
            (self.deg_to_rad(self.laser_intersection_degree_3), self.laser_intersection_distance_3),
            (self.deg_to_rad(self.laser_intersection_degree_4), self.laser_intersection_distance_4),
            (self.deg_to_rad(self.laser_intersection_degree_5), self.laser_intersection_distance_5),
        ]
        camera_focal_length_mm = float(self.camera_focal_length_mm)
        sensor_size = (float(self.sensor_size_x_mm), float(self.sensor_size_y_mm))
        focal_point_to_center = float(self.focal_point_to_center)
        return HardwareConfiguration(
            camera_focal_length_mm,
            sensor_size,
            focal_point_to_center,
            intersections_rad_mm)

    def dismiss(self):
        super(HardwareConfig, self).dismiss()
        self._save()
        pop = LoadingBox(self.scanner, self.hardware())
        pop.open()


class LoadingBox(Popup):
    def __init__(self, scanner, hardware, **kwargs):
        self.scanner = scanner
        self.hardware = hardware
        super(LoadingBox, self).__init__(**kwargs)
        self.load_hardware()

    def load_hardware(self):
        threading.Thread(target=self.scanner.configure, args=(self.hardware, self.call_back)).start()

    def call_back(self,):
        Clock.schedule_once(self.dismiss)

    def dismiss(self, *largs):
        super(LoadingBox, self).dismiss()
