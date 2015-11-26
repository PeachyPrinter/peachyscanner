import kivy
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock


kivy.require('1.9.0')

Builder.load_file('ui/laserdetection.kv')

class SimpleColorPicker(BoxLayout):
    pass

class LaserDetection(Screen):
    capture = ObjectProperty()

    color = StringProperty('red')
    threshold = NumericProperty(225)

    def __init__(self, scanner, **kwargs):
        self.section = 'laserdetection'
        self.scanner = scanner
        Config.adddefaultsection(self.section)
        super(LaserDetection, self).__init__(**kwargs)
        Clock.schedule_once(self._load)

    def _load(self, *largs):
        self.color = Config.getdefault(self.section, 'laser_color', 'red')
        self.on_color(self, self.color)
        self.threshold = Config.getdefaultint(self.section, 'threshold', 225)

    def on_color(self, instance, value):
        self.ids[self.color].state = 'down'
        Config.set(self.section, 'laser_color', self.color)
        self._update_detector()

    def on_threshold(self, instance, value):
        Config.set(self.section, 'threshold', int(self.threshold))
        self._update_detector()

    def _update_detector(self):
        self.scanner.configure_laser_detector2(int(self.threshold), self.color)

    def save(self):
        Logger.info("Saving Laser Detection Info")
        Config.write()
