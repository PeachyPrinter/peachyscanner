import numpy as np


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

    def write_polar_points(self, polar_array, file_path):
        with open(file_path, 'w') as output:
            verticies = np.count_nonzero(polar_array)
            output.write("""ply
                            format ascii 1.0
                            comment made by Peachy Scanner
                            comment Date Should Go Here
                            element vertex {}
                            property float x
                            property float y
                            property float z
                            end_header""".format(verticies))
            degrees_per = polar_array.shape[0] / 360
            for idx_phi in range(0, polar_array.shape[0]):
                z_data = polar_array[idx_phi]
                for z in range(0, z_data.shape[0]):
                    (x, y) = self.pol2cart(z_data[z], degrees_per * idx_phi)
                    output.write('{} {} {}'.format(x, y, z))
