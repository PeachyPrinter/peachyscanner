import numpy as np
import logging

logger = logging.getLogger('peachy')

class PointConverter(object):
    def __init__(self):
        pass

    def get_points(self, frame, center):
        roi = frame
        maxindex = np.argmax(roi, axis=1)
        data = (np.ones(maxindex.shape[0]) * center) - maxindex
        data[data < 0] = 0
        data[data == center] = 0
        return data


class GLConverter(object):
    '''Takes Array Data from captured points and converts to normalized gl verticies'''

    def convert(self, polar_array, scale=1.0):
        if not len(polar_array):
            return []
        sections = polar_array.shape[0]
        rad_per = (2.0 * np.pi) / sections
        xi = np.reshape(np.cos(np.arange(0,(2.0 * np.pi),rad_per)), (sections,-1))
        yi = np.reshape(np.sin(np.arange(0,(2.0 * np.pi),rad_per)), (sections,-1))
        x = (xi * polar_array) * scale
        y = (yi * polar_array) * scale
        z = (np.array([np.arange(polar_array.shape[1])]) * np.ones(polar_array.shape)) * scale
        a = np.ones(polar_array.shape) * xi
        b = np.ones(polar_array.shape) * yi
        c = np.zeros(x.shape)
        u = np.ones(polar_array.shape) * np.reshape(np.arange(0,sections), (sections,-1))
        v = z

        xyz = np.dstack((x,y,z,a,b,c,u,v)).flatten()
        xyz = np.array(np.hsplit(xyz, xyz.shape[0] // 8))
        xyz = xyz[np.logical_not(np.logical_and(np.isclose(xyz[:,0], 0.0), np.isclose(xyz[:,1], 0.0), np.isclose(xyz[:,2], 0.0),))]
        return xyz.flatten()