import numpy as np
import logging
import time

logger = logging.getLogger('peachy')

from point_converter import GLConverter

class Writer(object):
    def write_points(self, array):
        pass


class PLYWriter(Writer):

    def __init__(self):
        self.converter = GLConverter()

    def write_polar_points(self, outfile, polar_array):
        start = time.time()
        points = self.converter.convert(polar_array)
        verticies = points.shape[0] / 8
        

        header = "ply\nformat ascii 1.0\ncomment made by Peachy Scanner\ncomment Date Should Go Here\nelement vertex {}\nproperty float x\nproperty float y\nproperty float z\nend_header\n".format(str(verticies))

        outfile.write(header)

        for (x, y, z, a, b, c, u, v) in np.hsplit(points, points.shape[0] // 8):
            outfile.write('{} {} {}\n'.format(x, y, z))

        total = time.time() - start

        logger.info('File Written in {:.2f} milliseconds'.format(total * 1000.0))
