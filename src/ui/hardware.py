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
    laser_intersection_degree = BoundedNumericProperty(45.0, min=0.0, max=90.0)

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
        self.laser_intersection_degree = float(Config.getdefault(self.section, 'laser_intersection_degree', '45.0'))

    def _save(self):
        Config.set(self.section, 'camera_focal_length_mm', float(self.camera_focal_length_mm))
        Config.set(self.section, 'sensor_size_x_mm', float(self.sensor_size_x_mm))
        Config.set(self.section, 'sensor_size_y_mm', float(self.sensor_size_y_mm))
        Config.set(self.section, 'focal_point_to_center', float(self.focal_point_to_center))
        Config.set(self.section, 'laser_intersection_degree', float(self.laser_intersection_degree))
        Config.write()

    def hardware(self):
        rads = float(self.laser_intersection_degree) / 360 * 2 * np.pi
        camera_focal_length_mm = float(self.camera_focal_length_mm)
        sensor_size = (float(self.sensor_size_x_mm), float(self.sensor_size_y_mm))
        focal_point_to_center = float(self.focal_point_to_center)
        return HardwareConfiguration(
            camera_focal_length_mm,
            sensor_size,
            focal_point_to_center,
            rads)

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
