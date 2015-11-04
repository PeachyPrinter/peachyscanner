import numpy as np
from math import sin, cos, pi

center_of_rotation_x = 5 #distance to center
t = pi / 4.0 #Angle
focal_length = 5

pixels_x = sin(t) * 2
pixels_y = 0

center = np.array([center_of_rotation_x, 0, 0])

plane_p1 = np.array([center_of_rotation_x, 0, 0])
plane_p2 = np.array([center_of_rotation_x - cos(t), 0, sin(t)])
plane_p3 = np.array([center_of_rotation_x, 1, 0])

plane_v1 = plane_p3 - plane_p1
plane_v2 = plane_p2 - plane_p1

crossp = np.cross(plane_v1, plane_v2)

plane_a, plane_b, plane_c = crossp

plane_d = np.dot(crossp, plane_p3)

print('The plane equation is {0}x + {1}y + {2}z = {3}'.format(plane_a, plane_b, plane_c, plane_d))


plane_intersection_y = pixels_x
plane_intersection_z = pixels_x
plane_intersection_x = (plane_d - plane_intersection_z * plane_c - plane_b * plane_intersection_y) / plane_a

intersect = np.array([plane_intersection_x, plane_intersection_y, plane_intersection_z])

print('The plane is intersected at {0}x + {1}y + {2}z '.format(*intersect))

dist = np.linalg.norm(np.array([intersect[0], intersect[2]]) - np.array([center[0], center[2]]))

print('The polar radius is {}'.format(dist))
# -------------------------------------------------------------

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x = np.linspace(0, 6, 100)
y = np.linspace(0, 6, 100)
X, Y = np.meshgrid(x, y)

Z = (plane_d - plane_a * X - plane_b * Y) / plane_c


# plot the mesh. Each array is 2D, so we flatten them to 1D arrays
ax.plot(X.flatten(),
        Y.flatten(),
        Z.flatten(), 'r. ')

# plot the original points. We use zip to get 1D lists of x, y and z
# coordinates.
ax.plot(*zip(plane_p1, plane_p2, plane_p3), color='r', linestyle=' ', marker='o')

ax.plot([0, center_of_rotation_x], [0, 0], color='g', linestyle='-', marker='d')
ax.plot([0, plane_intersection_x], [0, plane_intersection_y], [0, plane_intersection_z], color='k', linestyle='-', marker='d')

# adjust the view so we can see the point/plane alignment
ax.view_init(0, 22)
plt.tight_layout()
# plt.savefig('images/plane.png')
plt.show()