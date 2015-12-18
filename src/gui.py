import os

import numpy as np
import threading 

import kivy
from kivy.app import App
from kivy.config import Config, ConfigParser
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.resources import resource_add_path
from kivy.logger import Logger
from kivy.clock import Clock

from infrastructure.hardware import HardwareConfiguration

from ui.camera import CameraControls
from ui.posisition import PositionControl
from ui.laserdetection import LaserDetection
from ui.capture_control import PointsCapture
from ui.video import ImageDisplay
from ui.hardware import HardwareConfig, HardwareLoader

kivy.require('1.9.0')


class SideBarScreenManager(ScreenManager):

    def __init__(self, scanner, video_widget, **kwargs):
        super(SideBarScreenManager, self).__init__(**kwargs)
        self.camera_control_ui = CameraControls(scanner.camera)
        self.posisition_control_ui = PositionControl(scanner, video_widget)
        self.laser_detection_ui = LaserDetection(scanner)
        self.points_capture_ui = PointsCapture(scanner)
        self.add_widget(self.camera_control_ui)
        self.add_widget(self.posisition_control_ui)
        self.add_widget(self.laser_detection_ui)
        self.add_widget(self.points_capture_ui)
        self.current = 'camera_control_ui'


class ScannerGUI(Screen):
    def __init__(self, scanner, **kwargs):
        self.scanner = scanner
        super(ScannerGUI, self).__init__(**kwargs)
        self.sub_manager = SideBarScreenManager(scanner, self.video)
        self.ids.screen_manager.add_widget(self.sub_manager)

    def start_config(self):
        self.sub_manager.current = 'camera_control_ui'
        self.manager.current = 'config'


class MasterGUI(ScreenManager):
    def __init__(self, scanner, **kwargs):
        self.scanner = scanner
        super(MasterGUI, self).__init__(**kwargs)
        self.scannergui = ScannerGUI(self.scanner)
        self.loading = LoadingBox(self.scanner)
        self.config = HardwareConfig(self.scanner)
        self.add_widget(self.scannergui)
        self.add_widget(self.loading)
        self.add_widget(self.config)
        self.current = 'loading'


class LoadingBox(Screen):
    def __init__(self, scanner, **kwargs):
        self.scanner = scanner
        super(LoadingBox, self).__init__(**kwargs)

    def on_enter(self):
        self.load_hardware()

    def load_hardware(self):
        hardware = HardwareLoader.get_hardware()
        threading.Thread(target=self.scanner.configure, args=(hardware, self.call_back)).start()

    def call_back(self,):
        self.parent.current = 'scanner_gui_screen'



class PeachyScannerApp(App):
    button_height = NumericProperty(dp(40))
    label_height = NumericProperty(dp(30))
    input_height = NumericProperty(dp(30))
    refresh_rate = NumericProperty(1.0 / 30.0)
    Config = ConfigParser(name='PeachyScanner')
    scanner = ObjectProperty()

    def __init__(self, scanner, **kwargs):
        Window.size = (1024, 500)
        Window.minimum_width = 900
        Window.minimum_height = 600
        Window.x = 0
        Window.y = 0
        resource_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
        resource_add_path(resource_path)
        resource_add_path(os.path.join(resource_path, 'shaders'))
        resource_add_path(os.path.join(resource_path, 'images'))
        self.scanner = scanner
        super(PeachyScannerApp, self).__init__(**kwargs)
        Config.set("input", "mouse", "mouse,disable_multitouch")
        Config.set("kivy", "exit_on_escape", 0)
        Logger.info("Starting up")

    def build(self):
        return(MasterGUI(self.scanner))

    def exit_app(self, *args):
        self.shutdown()

    def shutdown(self, *args):
        exit()
