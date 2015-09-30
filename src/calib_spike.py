import numpy as np
import cv2
from cv2.cv import *
import glob
import time

grid_x = 9
grid_y = 6

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((grid_x*grid_y, 3), np.float32)
objp[:, :2] = np.mgrid[0:grid_x, 0:grid_y].T.reshape(-1, 2)

images = glob.glob('*.png')
print "Got %s images" % images

running = True
show_result = False

NamedWindow('frame', flags=CV_WINDOW_NORMAL)
cv2.resizeWindow('frame', 960, 540)


cap = cv2.VideoCapture(0)
cap.read()
cap.set(CV_CAP_PROP_FRAME_HEIGHT, 1080.0)
cap.set(CV_CAP_PROP_FRAME_WIDTH, 1920.0)

start = time.time()
while running:
    objpoints = []
    imgpoints = []
    total = time.time() - start
    print('FPS: {}'.format(1.0 / total))
    start = time.time()
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (grid_x, grid_y), flags=cv2.CALIB_CB_FAST_CHECK)
    if ret is True:
        objpoints.append(objp)
        cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)
        cv2.drawChessboardCorners(img, (grid_x, grid_y), corners, ret)

        if not show_result:
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
            h,  w = img.shape[:2]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    if show_result:
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        if dst.shape[0] > 1:
            img = dst

    cv2.imshow('frame', img)
    key = chr(cv2.waitKey(1) & 0xFF)
    if key == 'q':
        running = False
    if key == 't':
        show_result = not show_result

cv2.destroyAllWindows()
cap.release()
