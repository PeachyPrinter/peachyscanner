from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.resources import resource_find
from kivy.graphics.opengl import GL_DEPTH_TEST, glEnable, glDisable
from kivy.graphics.transformation import Matrix
from kivy.graphics import BindTexture, Scale, Fbo, Rectangle, Canvas, Callback, ClearColor, RenderContext, Callback, ClearBuffers, PushMatrix, PopMatrix, Color, Translate, Rotate, UpdateNormalMatrix, Mesh, Line
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from threading import Lock
from math import tan, atan

import numpy as np
import time

from infrastructure.gl_point_converter import GLConverter

Builder.load_file('ui/capture_control.kv')


class NumpyImage(BoxLayout):
    texture = ObjectProperty(None, allownone=True)
    tex_pos = ObjectProperty([0, 0])
    tex_size = ObjectProperty([1, 1])

    def _get_new_size(self, source_x, source_y):
        source_ratio = source_x / float(source_y)
        if self.width > 0 and self.height > 0:
            dest_ratio = self.width / float(self.height)
        else:
            dest_ratio = 1
        if dest_ratio > source_ratio:
            return (int(source_x * self.height / source_y), int(self.height))
        else:
            return (int(self.width), int(source_y * self.width / source_x))

    def set_image(self, value):
        image = np.rot90(np.swapaxes(value, 0, 1))
        if self.texture is None:
            self.texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        self.texture.blit_buffer(image.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        self.tex_size = self._get_new_size(self.texture.size[0], self.texture.size[1])
        self.tex_pos = (self.x + (self.width - self.tex_size[0]) / 2, self.y + (self.height - self.tex_size[1]) / 2)

    def on_size(self, instance, value):
        if self.texture is not None:
            self.tex_size = self._get_new_size(self.texture.size[0], self.texture.size[1])
            self.tex_pos = (self.x + (self.width - self.tex_size[0]) / 2, self.y + (self.height - self.tex_size[1]) / 2)


class ImageCapture(Screen):

    def __init__(self, scanner, **kwargs):
        super(ImageCapture, self).__init__(**kwargs)
        self.scanner = scanner

    def start_image_capture(self):
        self._disable_all()
        self.scanner.capture_image(self._capture_image_callback)

    def _capture_image_callback(self, handler):
        self._image = handler.image
        if handler.complete:
            self._enable_all()
        Clock.schedule_once(self._update_image)

    def _update_image(self, *args):
        self.image_box.set_image(self._image)

    def _enable_all(self):
        self.ids['capture_button'].disabled = False

    def _disable_all(self):
        self.ids['capture_button'].disabled = True


class PointsCapture(Screen):
    def __init__(self, scanner, **kwargs):
        super(PointsCapture, self).__init__(**kwargs)
        self.scanner = scanner
        self._converter = GLConverter()
        self.raw_points_tyr = np.array([])

    def start_points_capture(self):
        self._disable_all()
        self.scanner.capture_points(self._capture_points_callback)
        self.scanner.capture_image(self._capture_image_callback, 200 - 31 )

    def _capture_image_callback(self, handler):
        self._image = handler.image
        Clock.schedule_once(self._update_image)

    def _capture_points_callback(self, handler):
        self.raw_points_tyr = handler.points_tyr
        self.progress.value = int(handler.status * 100)
        if handler.complete:
            self._enable_all()
            # Logger.info('Done: {}'.format(self.raw_points_tyr))
            from infrastructure.writer import PLYWriter
            with open('out.ply', 'w') as afile:
                PLYWriter().write_polar_points(afile, self.raw_points_tyr)
        Clock.unschedule(self.update_model)
        Clock.schedule_once(self.update_model)

    def _enable_all(self):
        self.go_button.disabled = False

    def _disable_all(self):
        self.go_button.disabled = True

    def _update_image(self, *args):
        if hasattr(self, '_image'):
            self.image_box.set_image(self._image)
            self.render.update_texture(self.image_box.texture)

    def update_model(self, *largs):
        amax = np.amax(self.raw_points_tyr)
        if amax > 0:
            scale = min(0.05, 1.0 / np.amax(self.raw_points_tyr))
            points = self._converter.convert(self.raw_points_tyr, scale=scale)
            self.render.update_mesh(points)


class ObjectRenderer(BoxLayout):
    texture = ObjectProperty(None, allownone=True)
    mesh_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.lock = Lock()
        self.gl_depth = -3
        self.mesh_data = MeshData()
        self.mesh_data.vertices = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        self.mesh_data.indices = np.array([0])
        self.points = None

        self.canvas = Canvas()
        with self.canvas:
            self.fbo = Fbo(size=(10, 10), compute_normal_mat=True)
            self.fbo.add_reload_observer(self.populate_fbo)
        with self.fbo:
            ClearColor(1, 1, 1, 1)
            ClearBuffers()

        self.populate_fbo(self.fbo)

        super(ObjectRenderer, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_glsl, 1 / 10.)

    def on_size(self, instance, value):
        size = (max(1, value[0]), max(1, value[1]))
        self.fbo.size = size
        self.texture = self.fbo.texture

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_texture(self, texture):
        if not hasattr(self, 'model_texture'):
            self.model_texture = texture
            self.populate_fbo(self.fbo)

    def update_glsl(self, *largs):
        # self.fbo.shader.source = resource_find('simple.glsl')
        asp = max(10,self.size[0]) / max(10, float(self.size[1]))
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        model = Matrix().look_at(   0.0, 0.0, 0.0,   0.0, 0.0, -3.0,   0.0, 1.0, 0.0)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        with self.canvas:
            self.fbo['projection_mat'] = proj
            self.fbo['modelview_mat'] = model
        with self.lock:
            self.mesh.vertices = self.mesh_data.vertices
            self.mesh.indices = self.mesh_data.indices
        self.rot.angle += -3

    def update_mesh(self, points):
        self.points = points
        #TODO make this dynamic or something
        points = np.array(np.hsplit(points, points.shape[0] // 8)).flatten()

        with self.lock:
            self.mesh_data.vertices = points
            indicies = np.arange(len(points) // 8)
            if self.mesh_mode:
                idx = []
                y = 0
                x = 0
                z = 0
                for pos in range(1, len(indicies)):
                    if points[(indicies[pos] * 8) + 2] > z:
                        A = indicies[pos - 1]
                        B = indicies[pos]
                        idx.extend([A, B])
                    (x,y,z) = points[(indicies[pos] * 8) : (indicies[pos] * 8 ) + 3]

                self.mesh_data.indices = idx
                self.mesh.mode = 'lines'
            else:
                self.mesh_data.indices = indicies
                self.mesh.mode = 'points'

    def populate_fbo(self, fbo):
        with self.canvas:
            fbo.shader.source = resource_find('simple.glsl')
            fbo['diffuse_light'] = (1.0, 1.0, 0.8)
            fbo['ambient_light'] = (0.5, 0.5, 0.5)
        
        with fbo:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            if hasattr(self, 'model_texture'):
                BindTexture(texture=self.model_texture, index=1)
            Translate(0, 0, self.gl_depth  + 1)
            Rotate(90, 1, 0, 0)
            self.rot = Rotate(1, 0, 0, 1)
            UpdateNormalMatrix()
            Color(1, 1, 1, 1)
            self.mesh = Mesh(
                    vertices=self.mesh_data.vertices,
                    indices=self.mesh_data.indices,
                    fmt=self.mesh_data.vertex_format,
                    mode=self.mesh_data.mode,
                )
            PopMatrix()
            # PushMatrix()
            # Translate(0, 0, self.gl_depth)
            # Rotate(90, 1, 0, 0)
            # self.rot
            # UpdateNormalMatrix()
            # self.show_axis()   #Help with GL alignments
            # PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        fbo['texture1'] = 1

    def show_axis(self):
        Color(1, 1, 0, 1) #Yellow
        Mesh(
                vertices=[
                     -1,        0,      0, 1, 1, 0, 0, 0,
                      1,        0,      0, 1, 1, 0, 0, 0,
                    0.8,      0.1,      0, 1, 1, 0, 0, 0,
                    0.8,     -0.1,      0, 1, 1, 0, 0, 0,
                      1,        0,      0, 1, 1, 0, 0, 0,
                    0.8,        0,   -0.1, 1, 1, 0, 0, 0,
                    0.8,        0,    0.1, 1, 1, 0, 0, 0,
                      1,        0,      0, 1, 1, 0, 0, 0,
                  ],
                indices=[0, 1, 2, 3, 4, 5, 6, 7],
                fmt=self.mesh_data.vertex_format,
                mode='line_strip',
            )
        Color(1, 0, 1, 1) # purple
        Mesh(
                vertices=[
                       0,      0,      -1, 0, 1, 1, 0, 0,
                       0,      0,       1, 0, 1, 1, 0, 0,
                     0.1,      0,     0.8, 0, 1, 1, 0, 0,
                    -0.1,      0,     0.8, 0, 1, 1, 0, 0,
                       0,      0,       1, 0, 1, 1, 0, 0,
                       0,   -0.1,     0.8, 0, 1, 1, 0, 0,
                       0,    0.1,     0.8, 0, 1, 1, 0, 0,
                       0,      0,       1, 0, 1, 1, 0, 0,
                  ],
                indices=[0, 1, 2, 3, 4, 5, 6, 7],
                fmt=self.mesh_data.vertex_format,
                mode='line_strip',
            )
        Color(0, 1, 1, 1) # Baby Blue
        Mesh(
                vertices=[
                       0,      -1,      0, 1, 1, 0, 0, 0,
                       0,       1,      0, 1, 1, 0, 0, 0,
                     0.1,     0.8,      0, 1, 1, 0, 0, 0,
                    -0.1,     0.8,      0, 1, 1, 0, 0, 0,
                       0,       1,      0, 1, 1, 0, 0, 0,
                       0,     0.8,   -0.1, 1, 1, 0, 0, 0,
                       0,     0.8,    0.1, 1, 1, 0, 0, 0,
                       0,       1,      0, 1, 1, 0, 0, 0,
                  ],
                indices=[0, 1, 2, 3, 4, 5, 6, 7],
                fmt=self.mesh_data.vertex_format,
                mode='line_strip',
            )

    def on_mesh_mode(self, instance, value):
        self.update_mesh(self.points)

class MeshData(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        self.vertices = []
        self.indices = []
        self.mode = 'points'