import os

import kivy
from kivy.app import App
from kivy.config import Config, ConfigParser
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.resources import resource_add_path, resource_find
from kivy.logger import Logger
from kivy.graphics.opengl import GL_DEPTH_TEST, glEnable, glDisable
from kivy.graphics.transformation import Matrix
from kivy.graphics import Fbo, Rectangle, Canvas, Callback, ClearColor, ClearBuffers, PushMatrix, PopMatrix, Color, Translate, Rotate, UpdateNormalMatrix, Mesh, Line
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import time
import numpy as np

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


class Main(BoxLayout):
    pass

class GLWindow(BoxLayout):
    texture = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self.mesh_data = MeshData()
        self.canvas = Canvas()
        with self.canvas:
            self.fbo = Fbo(size=(10, 10), compute_normal_mat=True)
            self.fbo.add_reload_observer(self.populate_fbo)
        with self.fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
        self.populate_fbo(self.fbo)

        super(GLWindow, self).__init__(**kwargs)

        Clock.schedule_interval(self.update_glsl, 1 / 60.)

    def populate_fbo(self, fbo):
        Logger.info("Setting up FBO")

        with self.canvas:
            fbo.shader.source = resource_find('simple.glsl')
            fbo['diffuse_light'] = (1.0, 1.0, 0.8)
            fbo['ambient_light'] = (0.8, 0.8, 0.8)

        with fbo:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            UpdateNormalMatrix()
            Translate(0,0,-3)
            self.rot = Rotate(1,0,1,0)
            # self.show_axis()
            self.make_pretty_dots()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)

    def update_glsl(self, *largs):
        asp = self.size[0] / float(self.size[1])
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        model = Matrix().look_at(   0.0, 0.0, 0.25,   0.0, 0.0, 0.0,   0.0, 1.0, 0.0)
        with self.canvas:
            self.fbo['projection_mat'] = proj
            self.fbo['modelview_mat'] = model
            self.rot.angle += -1
            self.texture = self.fbo.texture

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def on_size(self, instance, value):
        Logger.info('resize')
        self.fbo.size = value
        self.texture = self.fbo.texture

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

    def make_pretty_dots(self):
        points_per_side = 50

        points = []
        for idx in range(points_per_side):
            v = -1.0 + ((2.0 / points_per_side) * float(idx))
            tex = idx / float(points_per_side)
            points.append(
                [
                [ v,  -1.0,  -1.0,    v,  -1.0,  -1.0,     tex,  0.0],
                [ v,  -1.0,   1.0,    v,  -1.0,   1.0,     tex,  0.0],
                [ v,   1.0,  -1.0,    v,   1.0,  -1.0,     tex,  1.0],
                [ v,   1.0,   1.0,    v,   1.0,   1.0,     tex,  1.0],
                [ -1.0,  v,  -1.0,    -1.0,  v,  -1.0,     0.0,  tex],
                [ -1.0,  v,   1.0,    -1.0,  v,   1.0,     0.0,  tex],
                [  1.0,  v,  -1.0,     1.0,  v,  -1.0,     1.0,  tex],
                [  1.0,  v,   1.0,     1.0,  v,   1.0,     1.0,  tex],
                [ -1.0,  -1.0,  v,    -1.0,  -1.0,  v,     tex,  tex],
                [ -1.0,   1.0,  v,    -1.0,   1.0,  v,     tex,  tex],
                [  1.0,  -1.0,  v,     1.0,  -1.0,  v,     tex,  tex],
                [  1.0,   1.0,  v,     1.0,   1.0,  v,     tex,  tex]],
                )

        points = np.array(points).flatten()
        Color(1,1,1,1)
        Mesh(
                vertices=points,
                indices=[i for i in range(len(points) / 8)],
                fmt=self.mesh_data.vertex_format,
                mode='points',
            )

class SpikeGlApp(App):
    Config = ConfigParser(name='Spikes')


    def __init__(self, **kwargs):
        Window.size = (1024, 500)
        Window.minimum_width = 900
        Window.minimum_height = 600
        Window.x = 0
        Window.y = 0
        resource_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
        resource_add_path(resource_path)
        resource_add_path(os.path.join(resource_path, 'shaders'))
        super(SpikeGlApp, self).__init__(**kwargs)
        Config.set("input", "mouse", "mouse,disable_multitouch")
        Config.set("kivy", "exit_on_escape", 0)
        Logger.info("Starting up")

    def build(self):
        return(Main())

    def exit_app(self, *args):
        self.shutdown()

    def shutdown(self, *args):
        exit()


if __name__ == '__main__':
    SpikeGlApp().run()