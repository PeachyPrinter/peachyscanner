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
    def select_centre(self):
        self._disable_all()
        App.get_running_app().capture.get_centre(self._points_cb)

    def _points_cb(self, pos):
        self._enable_all()
        Logger.info('Found centre: {}'.format(pos))

    def select_encoder(self):
        self._disable_all()
        App.get_running_app().capture.select_encoder(self._encoder_cb)

    def _encoder_cb(self, encoder_pos):
        self._enable_all()
        Logger.info('Found Encoder: {}'.format(encoder_pos))

    def select_roi(self):
        self._disable_all()
        App.get_running_app().capture.select_roi(self._roi_cb)

    def _roi_cb(self, roi):
        self._enable_all()
        Logger.info('Found ROI: {}'.format(roi))

    def _disable_all(self):
        for child in self.children:
            child.disabled = True

    def _enable_all(self):
        for child in self.children:
            child.disabled = False


class ColorControls(Screen):
    def __init__(self, **kwargs):
        super(ColorControls, self).__init__(**kwargs)
        self.visable = False
        self.ids.dark_color.bind(color=self._color_changed)
        self.ids.light_color.bind(color=self._color_changed)

    def _color_changed(self, instance, value):
        if self.visable:
            App.get_running_app().capture.show_range(list(self.ids.dark_color.color)[:3], list(self.ids.light_color.color)[:3])

    def toggle_mask(self, state):
        Logger.info("state: {}".format(state))
        if state == 'down':
            show = True
        else:
            show = False
        Logger.info("state: {}".format(state))
        App.get_running_app().capture.toggle_mask(show)

    def on_enter(self):
        self.visable = True
        # App.get_running_app().capture.show_range(self.ids.dark_color[:3], self.ids.light_color[:3])

    def on_leave(self):
        App.get_running_app().capture.hide_range()
        self.visable = False


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
        self.ids.focus.value = self.capture.camera.focus
        self.ids.brightness.value = self.capture.camera.brightness
        self.ids.contrast.value = self.capture.camera.contrast
        self.ids.white_balance.value = self.capture.camera.white_balance
        self.ids.sharpness.value = self.capture.camera.sharpness

    def on_focus(self, instance, value):
        self.capture.camera.focus = value

    def on_brightness(self, instance, value):
        self.capture.camera.brightness = value

    def on_contrast(self, instance, value):
        self.capture.camera.contrast = value

    def on_white_balance(self, instance, value):
        self.capture.camera.white_balance = value

    def on_sharpness(self, instance, value):
        self.capture.camera.sharpness = value


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
        Window.x = 0
        Window.y = 0
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

