import numpy as np
import logging
logger = logging.getLogger('peachy')


class GLConverter(object):
    '''Takes Array Data from captured points and converts to normalized gl verticies'''

    def convert(self, point_array_tyr, scale=1.0):
        if not len(point_array_tyr):
            return []
        sections = point_array_tyr.shape[0]
        rad_per = (2.0 * np.pi) / sections
        xi = np.reshape(np.cos(np.arange(0, (2.0 * np.pi), rad_per)), (sections, -1))
        yi = np.reshape(np.sin(np.arange(0, (2.0 * np.pi), rad_per)), (sections, -1))
        x = (xi * point_array_tyr) * scale
        y = (yi * point_array_tyr) * scale
        z = (np.array([np.arange(point_array_tyr.shape[1])]) * np.ones(point_array_tyr.shape)) * scale
        a = np.ones(point_array_tyr.shape) * xi
        b = np.ones(point_array_tyr.shape) * yi
        c = np.zeros(x.shape)
        u = np.ones(point_array_tyr.shape) * np.reshape(np.arange(0, sections), (sections, -1)) / sections
        v = np.ones(z.shape) - (z.copy() / np.amax(z))
        xyz = np.dstack((x, y, z, a, b, c, u, v))
        xyz = xyz.reshape(xyz.size / 8, 8)
        return xyz
