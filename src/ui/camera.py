import kivy
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock


kivy.require('1.9.0')

Builder.load_file('ui/camera.kv')


class CameraControl(BoxLayout):
    text = StringProperty()
    min_value = NumericProperty(0.0)
    max_value = NumericProperty(1.0)
    value = NumericProperty()

    def __init__(self, name, value, setter, **kwargs):
        self.text = name
        self.value = value
        self._setter = setter
        super(CameraControl, self).__init__(**kwargs)

    def on_value(self, instance, value):
        self._setter(self.text, value)


class CameraControls(Screen):
    capture = ObjectProperty()

    def __init__(self, camera, **kwargs):
        super(CameraControls, self).__init__(**kwargs)
        Config.adddefaultsection('camera')
        for setting in camera.get_settings():
            name = setting['name']
            value = setting['value']
            control = CameraControl(name, value, camera.set_setting)
            self.camera_control.add_widget(control, -1)

    def _load_saved_settings(self):
        pass

    def save(self):
        settings = {}
        for control in self.camera_control.children:
            settings[control.text] = control.value
        Logger.info(str(settings))


