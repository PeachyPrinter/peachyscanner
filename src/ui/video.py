from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.graphics import Color, Line

import cv2

import numpy as np

Builder.load_file('ui/video.kv')


class ImageDisplay(BoxLayout):
    scanner = ObjectProperty()
    texture = ObjectProperty(Texture.create(size=(1, 1), colorfmt='rgb'))
    video_pos = ListProperty([0, 0])
    video_size = ListProperty([1, 1])
    show_encoder = BooleanProperty(True)
    show_encoder_history = BooleanProperty(True)
    show_roi = BooleanProperty(True)
    show_mask = BooleanProperty(True)
    show_center = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(ImageDisplay, self).__init__(**kwargs)
        with self.canvas.after:
            Color(1., 0., 0)
            self.ret = Line(rectangle=(0, 0, 0, 0))
            Color(1, 1, 1)
            self.center_line = Line(points=[0, 0, 0, 0], width=1)

        Clock.schedule_interval(self.update_image, 1 / 30.)

    def _add_overlays_to_image(self, image, overlays):
        img2gray = cv2.cvtColor(overlays, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
        image = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))
        return cv2.add(image, overlays)

    def _image_to_texture(self, image):
        image = np.rot90(np.swapaxes(image, 0, 1))
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        texture.blit_buffer(image.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        return texture

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
        if self.show_roi:
            image = image_data['roi_frame']
        else:
            image = image_data['frame']
        overlays = np.zeros(image.shape, dtype=image.dtype)
        if self.show_encoder:
            overlays = cv2.add(overlays, image_data['encoder'])
        if self.show_encoder_history:
            overlays = cv2.add(overlays, image_data['history'])

        image = self._add_overlays_to_image(image, overlays)
        self.texture = self._image_to_texture(image)


    def selection(self, x, y, w, h):
        with self.canvas.after:
            self.ret.rectangle = (x, y, w, h)
