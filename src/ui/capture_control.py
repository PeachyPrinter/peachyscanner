from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.opengl import GL_DEPTH_TEST, glEnable, glDisable
from kivy.graphics.transformation import Matrix
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, Color, Translate, Rotate, UpdateNormalMatrix, Mesh
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from threading import Lock

import numpy as np
import time

from infrastructure.point_converter import GLConverter

Builder.load_file('ui/capture_control.kv')

class CaptureControl(Screen):

    def __init__(self, **kwargs):
        super(CaptureControl, self).__init__(**kwargs)
        App.get_running_app().status.register_handler(self.update_progress)
        self._converter = GLConverter()
        self.raw_points = np.array([])

    def start_points_capture(self):
        self._disable_all()
        App.get_running_app().capture.start_capture(self._capture_callback)

    def _capture_callback(self, file_name):
        self._enable_all()

    def _enable_all(self):
        for child in self.children:
            child.disabled = False

    def _disable_all(self):
        for child in self.children:
            child.disabled = True

    def update_progress(self, status):
        self.raw_points = status.points
        self.progress.value = status.progress
        Clock.unschedule(self.update_model)
        Clock.schedule_once(self.update_model)

    def update_model(self, *largs):
        if len(self.raw_points) > 0:
            scale = min(0.05, 1.0 / np.amax(self.raw_points))
            points = self._converter.convert(self.raw_points, scale=scale)
            self.render.update_mesh(points)



class ObjectRenderer(Widget):
    def __init__(self, **kwargs):
        self.lock = Lock()
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        self.mesh_data = MeshData()
        self.mesh_data.vertices = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        self.mesh_data.indices = np.array([0])
        super(ObjectRenderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        Clock.schedule_interval(self.update_glsl, 1 / 10.)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj
        with self.lock:
            self.mesh.vertices = self.mesh_data.vertices
            self.mesh.indices = self.mesh_data.indices
        self.rot.angle += -3

    def update_mesh(self, points):
        #TODO make this dynamic or something
        points = np.array(np.hsplit(points, points.shape[0] // 8))[::4].flatten()
        with self.lock:
            self.mesh_data.vertices = points
            self.mesh_data.indices = np.arange(len(points) // 8)

    def setup_scene(self):
        self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
        self.canvas['ambient_light'] = (0.1, 0.1, 0.1)
        Color(1, 0, 0, 1)
        PushMatrix()
        Translate(0, 0, -3)
        Translate(0, 1, 0)
        Rotate(90, 1, 0, 0)
        self.rot = Rotate(1, 0, 0, 1)
        UpdateNormalMatrix()
        self.mesh = Mesh(
                vertices=self.mesh_data.vertices,
                indices=self.mesh_data.indices,
                fmt=self.mesh_data.vertex_format,
                mode='points',
            )
        PopMatrix()

class MeshData(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        self.vertices = []
        self.indices = []