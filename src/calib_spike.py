import numpy as np
import cv2, cv
import glob
import time

grid_x = 9
grid_y = 6

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((grid_x*grid_y, 3), np.float32)
objp[:, :2] = np.mgrid[0:grid_x, 0:grid_y].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('*.png')
print "Got %s images" % images

running = True

cv.NamedWindow('frame', flags=cv.CV_WINDOW_NORMAL)
cv2.resizeWindow('frame', 960, 540)


cap = cv2.VideoCapture(0)
cap.read()
cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 1080.0)
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 1920.0)

start = time.time()
while running:
    total = time.time() - start
    print('FPS: {}'.format(1.0 / total))
    start = time.time()
    ret, img = cap.read()
    # img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('img', gray)
    # cv2.waitKey(500)

    # print "Find the chess board corners"
    ret, corners = cv2.findChessboardCorners(gray, (grid_x, grid_y), flags=cv2.CALIB_CB_FAST_CHECK)
    
    # print "If found, add object points, image points (after refining them)"
    if ret is True:
        # print("Found corners")
        # objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (22, 22), (-1, -1), criteria)
        # imgpoints.append(corners2)

        print corners2

        # Draw and display the corners
        cv2.drawChessboardCorners(img, (grid_x, grid_y), corners, ret)
    cv2.imshow('frame', img)
    key = chr(cv2.waitKey(1) & 0xFF)
    if key == 'q':
        running = False

cv2.destroyAllWindows()
cap.release()
