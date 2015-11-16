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
    errosion_y = NumericProperty(3)
    errosion_x = NumericProperty(3)

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
        self.errosion_x = Config.getdefaultint(self.section, 'errosion_x', 3)
        self.errosion_y = Config.getdefaultint(self.section, 'errosion_y', 3)

    def on_color(self, instance, value):
        Logger.info("HERE {}".format(self.color))
        self.ids[self.color].state = 'down'
        Config.set(self.section, 'laser_color', self.color)
        self._update_detector()

    def on_threshold(self, instance, value):
        Config.set(self.section, 'threshold', int(self.threshold))
        self._update_detector()

    def on_errosion_x(self, instance, value):
        Config.set(self.section, 'errosion_x', int(self.errosion_x))
        self._update_detector()

    def on_errosion_y(self, instance, value):
        Config.set(self.section, 'errosion_y', int(self.errosion_y))
        self._update_detector()

    def _update_detector(self):
        # Logger.info("Laser Detector Updated: {} , ({},{}), {}".format(self.threshold, int(self.errosion_x), int(self.errosion_y), self.color))
        self.scanner.configure_laser_detector2(int(self.threshold), (int(self.errosion_x), int(self.errosion_y)), self.color)

    def save(self):
        Logger.info("Saving Laser Detection Info")
        Config.write()
