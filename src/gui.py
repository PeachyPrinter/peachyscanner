import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, BoundedNumericProperty, ObjectProperty, StringProperty
from kivy.logger import Logger
from api.capture import Capture

kivy.require('1.9.0')


class Callback(object):
    pass


class PositionControl(Screen):
    pass


class ColorControls(Screen):
    pass


class CameraControl(BoxLayout):
    text = StringProperty()
    min_value = NumericProperty()
    max_value = NumericProperty()
    default_value = NumericProperty()

    def __init__(self, **kwargs):
        super(CameraControl, self).__init__(**kwargs)
        Logger.info(str(dir(kwargs.keys())))
        self.value = getattr(kwargs, 'value')


class CameraControls(Screen):
    focus = BoundedNumericProperty(120, min=0, max=255)
    brightness = BoundedNumericProperty(120, min=0, max=255)
    contrast = BoundedNumericProperty(120, min=0, max=255)
    capture = ObjectProperty()

    def get_focus(self):
        self.focus = self.capture.get_focus()

    def on_focus(self, instance, value):
        self.capture.set_focus(value)


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.camera_control_ui = CameraControls()
        self.posisition_control_ui = PositionControl()
        self.color_control_ui = ColorControls()
        self.add_widget(self.camera_control_ui)
        self.add_widget(self.posisition_control_ui)
        self.add_widget(self.color_control_ui)
        self.current = 'camera_control_ui'


class PeachyScannerApp(App):
    button_height = NumericProperty(dp(40))
    label_height = NumericProperty(dp(30))
    input_height = NumericProperty(dp(30))
    refresh_rate = NumericProperty(1.0 / 30.0)
    capture = ObjectProperty()

    def __init__(self, **kwargs):
        Window.size = (350, 900)
        Window.minimum_width = 450
        Window.minimum_height = 900
        super(PeachyScannerApp, self).__init__(**kwargs)
        Config.set("input", "mouse", "mouse,disable_multitouch")
        Config.set("kivy", "exit_on_escape", 0)
        Logger.info("Starting up")
        self.callback = Callback()
        self.start_camera()

    def start_camera(self):
        self.capture = Capture(self.callback)
        self.capture.start()

    def exit_app(self, *args):
        self.shutdown()

    def shutdown(self, *args):
        if self.capture:
            self.capture.shutdown()
        exit()

