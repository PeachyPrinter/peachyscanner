from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.resources import resource_find
from kivy.graphics.opengl import GL_DEPTH_TEST, glEnable, glDisable
from kivy.graphics.transformation import Matrix
from kivy.graphics import BindTexture, Scale, Fbo, Rectangle, Canvas, Callback, ClearColor, RenderContext, Callback, ClearBuffers, PushMatrix, PopMatrix, Color, Translate, Rotate, UpdateNormalMatrix, Mesh, Line
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from threading import Lock
import os

import numpy as np
from math import floor

from infrastructure.gl_point_converter import GLConverter
from infrastructure.point_thinning import PointThinner
from infrastructure.writer import PLYWriter

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
            return (floor(source_x * self.height / source_y), floor(self.height))
        else:
            return (floor(self.width), floor(source_y * self.width / source_x))

    def set_image(self, value):
        image = np.rot90(np.swapaxes(value, 0, 1))
        if self.texture is None:
            self.texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        self.texture.blit_buffer(image.flatten(), colorfmt='bgr', bufferfmt='ubyte')
        self.tex_size = self._get_new_size(self.texture.size[0], self.texture.size[1])
        self.tex_pos = (self.x + (self.width - self.tex_size[0]) / 2, self.y + (self.height - self.tex_size[1]) / 2)

    def on_size(self, instance, value):
        if self.texture is not None:
            self.tex_size = self._get_new_size(self.texture.size[0], self.texture.size[1])
            self.tex_pos = (self.x + (self.width - self.tex_size[0]) / 2, self.y + (self.height - self.tex_size[1]) / 2)

    def clear(self):
        self.texture = None


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    path = StringProperty(os.path.expanduser("~"))


class GoButton(Button):

    def __init__(self, rad_value, go_method, **kwargs):
        super(GoButton, self).__init__(**kwargs)
        self.rad_value = rad_value
        self.go_method = go_method


class PointsCapture(Screen):
    def __init__(self, scanner, **kwargs):
        super(PointsCapture, self).__init__(**kwargs)
        self.scanner = scanner
        self._converter = GLConverter()
        self.raw_points_xyz = np.array([])

    def on_pre_enter(self):
        self.go_buttons.clear_widgets()
        self.clear()
        laser_pos = [("{: 5.2f}".format(np.rad2deg(rad)), rad) for rad in self.scanner.get_scanner_posisitions()]
        for (human, rad) in laser_pos:
            button = GoButton(rad, self.start_points_capture, text=str(human))
            self.go_buttons.add_widget(button)

    def on_leave(self):
        self.go_buttons.clear_widgets()
        self.clear()

    def clear(self,):
        # self.image_box.clear()
        self.render.clear()
        self.raw_points_xyz = np.array([])

    def start_points_capture(self, theta):
        self._disable_all()
        points = self.raw_points_xyz if self.raw_points_xyz.size != 0 else None
        self.scanner.capture_points_xyz(theta, points=points, call_back=self._capture_points_callback)
        # self.scanner.capture_image(self._capture_image_callback, 200 - 25)

    # def _capture_image_callback(self, handler):
    #     self._image = handler.image
    #     Clock.schedule_once(self._update_image)

    def _capture_points_callback(self, handler):
        self.raw_points_xyz = handler.points_xyz
        self.progress.value = int(handler.status * 100)
        if handler.complete:
            self._enable_all()
            # Logger.info('Done: {}'.format(self.raw_points_tyr))
            self.save_button.disabled = False
        Clock.unschedule(self.update_model)
        Clock.schedule_once(self.update_model)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        content = SaveDialog(save=self.save_points, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save_points(self, path, filename):
        with open(os.path.join(path, filename), 'w') as afile:
            thinner = PointThinner()
            converter = GLConverter()
            PLYWriter(converter, thinner).write_cartisien_points(afile, self.raw_points_xyz)
        self.dismiss_popup()

    def _enable_all(self):
        self.go_buttons.disabled = False
        self.clear_button.disabled = False

    def _disable_all(self):
        self.go_buttons.disabled = True
        self.clear_button.disabled = True

    # def _update_image(self, *args):
    #     if hasattr(self, '_image'):
    #         self.image_box.set_image(self._image)
    #         self.render.update_texture(self.image_box.texture)

    def update_model(self, *largs):
        amax = np.amax(self.raw_points_xyz)
        if amax > 0:
            scale = min(0.05, 1.0 / np.amax(self.raw_points_xyz))

            points = self._converter.convert_xyz(self.raw_points_xyz, scale=scale)
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


    def clear(self):
        if hasattr(self, 'model_texture'):
            self.mesh_data.vertices = np.array([0, 0, 0, 0, 0, 0, 0, 0])
            self.mesh_data.indices = np.array([0])
            del self.model_texture

    def update_texture(self, texture):
        if not hasattr(self, 'model_texture'):
            self.model_texture = texture
            self.populate_fbo(self.fbo)

    def update_glsl(self, *largs):
        # self.fbo.shader.source = resource_find('simple.glsl')
        asp = max(10, self.size[0]) / max(10, float(self.size[1]))
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        model = Matrix().look_at(   0.0, 0.0, 0.0,   0.0, 0.0, -3.0,   0.0, 1.0, 0.0)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        with self.canvas:
            self.fbo['projection_mat'] = proj
            self.fbo['modelview_mat'] = model
        self.mesh.vertices = self.mesh_data.vertices
        self.mesh.indices = self.mesh_data.indices
        self.rot.angle += -3

    def update_mesh(self, points):
        self.points = points
        points = np.array(points)[::8]
        points = points.flatten()

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
            Translate(0, 1, self.gl_depth + 1)
            self.rot = Rotate(0, 0, 1, 0)
            UpdateNormalMatrix()
            Color(1, 1, 1, 1)
            self.mesh = Mesh(
                    vertices=self.mesh_data.vertices,
                    indices=self.mesh_data.indices,
                    fmt=self.mesh_data.vertex_format,
                    mode=self.mesh_data.mode,
                )
            PopMatrix()
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