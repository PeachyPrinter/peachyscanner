import kivy
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.logger import Logger

import json

kivy.require('1.9.0')

Builder.load_file('ui/laserdetection.kv')


class LaserDetection(Screen):
    capture = ObjectProperty()

    def __init__(self, **kwargs):
        self.section = 'laserdetection'
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
        self.capture.show_range(list(self.dark_color.color)[:3], list(self.light_color.color)[:3])

    def _color_changed(self, instance, value):
        Config.set(self.section, 'light_color', json.dumps(self.light_color.color))
        Config.set(self.section, 'dark_color', json.dumps(self.dark_color.color))
        self.capture.show_range(list(self.dark_color.color)[:3], list(self.light_color.color)[:3])

    def toggle_mask(self, state):
        Logger.info("state: {}".format(state))
        if state == 'down':
            show = True
        else:
            show = False
        Logger.info("state: {}".format(state))
        self.capture.toggle_mask(show)

    def save(self):
        Logger.info("Saving Laser Detection Info")
        Config.write()
