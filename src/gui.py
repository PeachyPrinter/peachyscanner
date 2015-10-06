import kivy
from kivy.app import App
from kivy.config import Config, ConfigParser
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty
from kivy.logger import Logger
from api.capture import Capture


from ui.camera import CameraControlWrapper
from ui.posisition import PositionControl
from ui.laserdetection import LaserDetection

kivy.require('1.9.0')


class CaptureControl(Screen):

    def start_capture(self):
        self._disable_all()
        App.get_running_app().capture.start_capture(self._capture_callback)

    def _capture_callback(self, file_name):
        self._enable_all()

    def _enable_all(self):
        for child in self.children:
            child.disabled = False

    def _disable_all(self):
        for child in self.children:
            child.disabled = True


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.camera_control_ui = CameraControlWrapper()
        self.posisition_control_ui = PositionControl()
        self.laser_detection_ui = LaserDetection()
        self.capture_control_ui = CaptureControl()
        self.add_widget(self.camera_control_ui)
        self.add_widget(self.posisition_control_ui)
        self.add_widget(self.laser_detection_ui)
        self.add_widget(self.capture_control_ui)
        self.current = 'camera_control_ui'


class PeachyScannerApp(App):
    button_height = NumericProperty(dp(40))
    label_height = NumericProperty(dp(30))
    input_height = NumericProperty(dp(30))
    refresh_rate = NumericProperty(1.0 / 30.0)
    Config = ConfigParser(name='PeachyScanner')
    capture = ObjectProperty()

    def __init__(self, capture, **kwargs):
        Window.size = (350, 900)
        Window.minimum_width = 450
        Window.minimum_height = 900
        Window.x = 0
        Window.y = 0
        self.capture = capture
        super(PeachyScannerApp, self).__init__(**kwargs)
        Config.set("input", "mouse", "mouse,disable_multitouch")
        Config.set("kivy", "exit_on_escape", 0)
        Logger.info("Starting up")

    def exit_app(self, *args):
        self.shutdown()

    def shutdown(self, *args):
        if self.capture:
            self.capture.shutdown()
        exit()