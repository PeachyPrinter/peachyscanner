import numpy as np
import time

camera_width = 1920
camera_height = 1080
repititions = 1000

print "Starting"
pre_computed_ray_plane_intersections =  np.random.random_sample((camera_width, camera_height, 3)).astype('float16')


time_elapsed = 0
for i in range(repititions):
    # print " {}".format(i),
    image_from_camera = np.random.randint(1, size=(camera_width, camera_height)).astype('bool')
    start = time.time()
    result = pre_computed_ray_plane_intersections[image_from_camera]
    time_total = time.time() -start
    # print time_total
    time_elapsed +=  time_total

print "\nCompelte"
print "Total Time: {}".format(time_elapsed)
print "Per second: {}".format(repititions / time_elapsed)
print "MilliSeconds per: {}".format((time_elapsed / repititions) * 1000)