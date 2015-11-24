from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.graphics import Color, Line

import cv2

import numpy as np
import time
from operator import mul

Builder.load_file('ui/video.kv')


class ImageDisplay(BoxLayout):
    scanner = ObjectProperty()
    texture = ObjectProperty(Texture.create(size=(1, 1), colorfmt='rgb'))
    video_pos = ListProperty([0, 0])
    video_size = ListProperty([1, 1])
    show_encoder = BooleanProperty(True)
    show_encoder_history = BooleanProperty(True)
    show_roi = BooleanProperty(True)
    show_laser_detector = BooleanProperty(True)
    show_center = BooleanProperty(True)
    laser_detector_color_bgr = np.array([255,0,0], dtype='uint8')


    def __init__(self, **kwargs):
        super(ImageDisplay, self).__init__(**kwargs)
        with self.canvas.after:
            Color(1., 0., 0)
            self.ret = Line(rectangle=(0, 0, 0, 0))
            Color(1, 1, 1)
            self.center_line = Line(points=[0, 0, 0, 0], width=1)
            Window.bind(on_motion=self.on_motion)

        Clock.schedule_interval(self.update_image, 1 / 24.)

    def _add_overlays_to_image(self, image, overlays):
        img2gray = cv2.cvtColor(overlays, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
        image = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))
        return cv2.add(image, overlays)

    def _set_texture_from_image(self, image):
        image = np.rot90(np.swapaxes(image, 0, 1))
        if image.shape[:2] != self.texture.size:
            self.texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        self.texture.blit_buffer(image.flatten(), colorfmt='bgr', bufferfmt='ubyte')

    def on_texture(self, instance, value):
        self.video_size = self.texture.size
        self.video_pos = (self.x + (self.width - self.video_size[0]) / 2, self.y + (self.height - self.video_size[1]) / 2)

        if self.show_center:
            center = self.video_pos[0] + (self.video_size[0] / 2)
            self.center_line.points = [center, self.video_pos[1], center, self.video_pos[1] + self.video_size[1]]
        else:
            self.center_line.points = [0, 0, 0, 0]

    def update_image(self, largs):
        image_data = self.scanner.get_feed_image(self.size)
        self.last_image = image_data['frame']
        if self.show_roi:
            image = image_data['roi_frame']
        else:
            image = image_data['frame']
        overlays = np.zeros(image.shape, dtype=image.dtype)
        if self.show_laser_detector:
            #This next line is the fastest way of populating an array with an array
            try:
                colormask = np.tile(self.laser_detector_color_bgr, reduce(mul,overlays.shape[:2])).reshape(overlays.shape)
                overlays = cv2.bitwise_and(colormask, colormask, mask=image_data['laser_detection'])
            except:
                pass
        if self.show_encoder:
            overlays = cv2.add(overlays, image_data['encoder'])
        if self.show_encoder_history:
            overlays = cv2.add(overlays, image_data['history'])
        image = self._add_overlays_to_image(image, overlays)
        self._set_texture_from_image(image)

    def on_motion(self, instance, etype, motion_event):
        frame_x = motion_event.pos[0] - self.video_pos[0]
        frame_y = motion_event.pos[1] - self.video_pos[1]
        if frame_x > 0 and frame_y > 0 and frame_x < self.width and frame_y < self.height:
            try:
                color = self.last_image[self.last_image.shape[0] - frame_y][frame_x]
            except:
                color = "FAIL"
            Logger.info(str(color[::-1]))

    def selection(self, x, y, w, h):
        with self.canvas.after:
            self.ret.rectangle = (x, y, w, h)
