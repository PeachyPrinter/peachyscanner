
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

import numpy as np

Builder.load_file('ui/video.kv')


class ImageDisplay(BoxLayout):
    scanner = ObjectProperty()
    image = ObjectProperty(Texture.create(size=(1, 1), colorfmt='rgb'))
    tex_pos = ListProperty([0, 0])
    tex_size = ListProperty([1, 1])

    def __init__(self, **kwargs):
        super(ImageDisplay, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_image, 1 / 30.)

    def update_image(self, largs):
        image = self.scanner.get_feed_image(self.size)['frame']
        image = np.rot90(np.swapaxes(image, 0, 1))
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        texture.blit_buffer(image.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        self.tex_size = texture.size
        self.tex_pos = (self.x + (self.width - self.tex_size[0]) / 2, self.y + (self.height - self.tex_size[1]) / 2)
        self.image = texture