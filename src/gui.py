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
from kivy.app import App

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
    value = NumericProperty()

    def __init__(self, **kwargs):
        super(CameraControl, self).__init__(**kwargs)


class CameraControls(Screen):
    capture = ObjectProperty()

    def __init__(self, **kwargs):
        super(CameraControls, self).__init__(**kwargs)
        self.get_capture_settings()
        self.ids.focus.bind(value=self.on_focus)
        self.ids.brightness.bind(value=self.on_brightness)
        self.ids.contrast.bind(value=self.on_contrast)
        self.ids.white_balance.bind(value=self.on_white_balance)
        self.ids.sharpness.bind(value=self.on_sharpness)

    def get_capture_settings(self):
        Logger.info('on_capture')
        self.ids.focus.value = self.capture.get_focus()
        self.ids.brightness.value = self.capture.get_brightness()
        self.ids.contrast.value = self.capture.get_contrast()
        self.ids.white_balance.value = self.capture.get_white_balance()
        self.ids.sharpness.value = self.capture.get_sharpness()

    def on_focus(self, instance, value):
        Logger.info('focus: {}'.format(value))
        self.capture.set_focus(value)

    def on_brightness(self, instance, value):
        Logger.info('brightness: {}'.format(value))
        self.capture.set_brightness(value)

    def on_contrast(self, instance, value):
        Logger.info('contrast: {}'.format(value))
        self.capture.set_contrast(value)

    def on_white_balance(self, instance, value):
        Logger.info('white_balance: {}'.format(value))
        self.capture.set_white_balance(value)

    def on_sharpness(self, instance, value):
        Logger.info('sharpness: {}'.format(value))
        self.capture.set_sharpness(value)



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

