import numpy as np
from numpy.lib.stride_tricks import as_strided

class ImageFiltering(object):

    def chunk_view(self, image, chunk):
        shape = (image.shape[0] - chunk[0] + 1, image.shape[1] - chunk[1] + 1) + chunk + (image.shape[2],)
        print image.strides
        strides = (image.strides[0], image.strides[1]) + image.strides
        print strides
        return as_strided(image, shape=shape, strides=strides)

    def averages(self, block):
        left = np.average(block, axis=0)
        up = np.average(left, axis=0)
        return up



a = np.array(
    [[[0,  0,  0], [0,    0, 64], [0,   0, 128], [0,   0, 192], [0,   0, 255]],
     [[0,  64, 0], [0,   64, 64], [0,  64, 128], [0,  64, 192], [0,  64, 255]],
     [[0, 128, 0], [0,  128, 64], [0, 128, 128], [0, 128, 192], [0, 128, 255]],
     [[0, 192, 0], [0,  192, 64], [0, 192, 128], [0, 192, 192], [0, 192, 255]],
     [[0, 255, 0], [0,  255, 64], [0, 255, 128], [0, 255, 192], [0, 255, 255]]],
     dtype='uint8'
    )

ifil = ImageFiltering()

b = ifil.chunk_view(a, (3, 3))
c = ifil.averages(b)


print "shape: {}".format(str(c.shape))
print "\n"
print "A\n {}".format(a[2, 2])
print "B\n {}".format(b[0, 0])
print "C\n {}".format(c[0, 0])


