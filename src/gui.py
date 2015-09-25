import kivy
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.logger import Logger
from api.capture import Capture

kivy.require('1.9.0')


class Callback(object):
    pass


class Control(object):
    def start_camera(self):
        self.capture = Capture(self.callback)
        self.capture.start()

    def focus_in(self):
        self.capture.focus_in()

    def focus_out(self):
        self.capture.focus_out()


class PeachyScannerApp(App, Control):
    button_height = NumericProperty(dp(40))
    label_height = NumericProperty(dp(30))
    input_height = NumericProperty(dp(30))
    refresh_rate = NumericProperty(1.0 / 30.0)

    def __init__(self, **kwargs):
        Window.size = (350, 900)
        Window.minimum_width = 350
        Window.minimum_height = 900
        super(PeachyScannerApp, self).__init__(**kwargs)
        Config.set("input", "mouse", "mouse,disable_multitouch")
        Config.set("kivy", "exit_on_escape", 0)
        Logger.info("Starting up")
        self.callback = Callback()
        self.start_camera()

    def exit_app(self, *args):
        self.shutdown()

    def shutdown(self, *args):
        if self.capture:
            self.capture.shutdown()
        exit()

