import kivy
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout

import json

kivy.require('1.9.0')

Builder.load_file('ui/laserdetection.kv')

class SimpleColorPicker(BoxLayout):
    pass

class LaserDetection(Screen):
    capture = ObjectProperty()

    def __init__(self, scanner, **kwargs):
        self.section = 'laserdetection'
        self.scanner = scanner
        Config.adddefaultsection(self.section)
        super(LaserDetection, self).__init__(**kwargs)
        self.visable = False
        self._load_colors()
        self.dark_color.bind(color=self._color_changed)
        self.light_color.bind(color=self._color_changed)

    def _load_colors(self):
        light = json.loads(Config.getdefault(self.section, 'light_color', '[255, 255, 255, 255]'))
        dark = json.loads(Config.getdefault(self.section, 'dark_color', '[0, 0, 0, 255]'))
        Logger.info("Loading light Color - {}".format(light))
        Logger.info("Loading dark Color - {}".format(dark))
        self.light_color.color = light
        self.dark_color.color = dark

    def _color_changed(self, instance, value):
        for idx in range(3):
            if self.light_color.color[idx] < self.dark_color.color[idx]:
                self.dark_color.color[idx] = self.light_color.color[idx]
        Config.set(self.section, 'light_color', json.dumps(self.light_color.color))
        Config.set(self.section, 'dark_color', json.dumps(self.dark_color.color))
        self.scanner.configure_laser_detector(list(self.dark_color.color)[:3], list(self.light_color.color)[:3])

    def save(self):
        Logger.info("Saving Laser Detection Info")
        Config.write()
