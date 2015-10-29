import os

import kivy
from kivy.app import App
from kivy.config import Config, ConfigParser
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.resources import resource_add_path
from kivy.logger import Logger


from ui.camera import CameraControls
from ui.posisition import PositionControl
from ui.laserdetection import LaserDetection
from ui.capture_control import CaptureControl
from ui.video import ImageDisplay

kivy.require('1.9.0')


class MyScreenManager(ScreenManager):

    def __init__(self, scanner, video_widget, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.camera_control_ui = CameraControls(scanner.camera)
        self.posisition_control_ui = PositionControl(scanner, video_widget)
        # self.laser_detection_ui = LaserDetection()
        self.capture_control_ui = CaptureControl(scanner)
        self.add_widget(self.camera_control_ui)
        self.add_widget(self.posisition_control_ui)
        # self.add_widget(self.laser_detection_ui)
        self.add_widget(self.capture_control_ui)
        self.current = 'camera_control_ui'


class ScannerGUI(BoxLayout):
    def __init__(self, scanner, **kwargs):
        super(ScannerGUI, self).__init__(**kwargs)
        self.manager = MyScreenManager(scanner, self.video)
        self.ids.screen_manager.add_widget(self.manager)


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
        self.scanner = scanner
        super(PeachyScannerApp, self).__init__(**kwargs)
        Config.set("input", "mouse", "mouse,disable_multitouch")
        Config.set("kivy", "exit_on_escape", 0)
        Logger.info("Starting up")

    def build(self):
        return(ScannerGUI(self.scanner))

    def exit_app(self, *args):
        self.shutdown()

    def shutdown(self, *args):
        exit()
