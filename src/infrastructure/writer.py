import numpy as np
import logging

logger = logging.getLogger('peachy')


class Writer(object):
    def write_points(self, array):
        pass


class PLYWriter(Writer):

    def cart2pol(self, x, y):
        rho = np.sqrt(x**2 + y**2)
        phi = np.arctan2(y, x)
        return(rho, phi)

    def pol2cart(self, rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return(x, y)

    def write_polar_points(self, outfile, polar_array):
        verticies = (polar_array >= 0).sum()
        sections = polar_array.shape[0]
        logger.info('Sections - {}'.format(sections))
        degrees_per = (2.0 * np.pi) / sections
        logger.info('Radians per point - {}'.format(degrees_per))

        header = "ply\nformat ascii 1.0\ncomment made by Peachy Scanner\ncomment Date Should Go Here\nelement vertex {}\nproperty float x\nproperty float y\nproperty float z\nend_header\n".format(str(verticies))

        outfile.write(header)

        for idx_phi in range(0, sections):
            z_data = polar_array[idx_phi]
            for z in range(0, z_data.shape[0]):
                if z_data[z] != -1:
                    (x, y) = self.pol2cart(z_data[z], degrees_per * idx_phi)
                    outfile.write('{} {} {}\n'.format(x, y, z))
