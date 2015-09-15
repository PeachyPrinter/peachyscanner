import numpy as np
import cv2, cv

cv.NamedWindow('frame', flags=cv.CV_WINDOW_NORMAL)
cv2.resizeWindow('frame', 1000, 700)

cap = cv2.VideoCapture(0)
cap.set(37, 1);
video_properties = {
    "CV_CAP_PROP_POS_MSEC": cv.CV_CAP_PROP_POS_MSEC,
    "CV_CAP_PROP_POS_FRAMES": cv.CV_CAP_PROP_POS_FRAMES,
    "CV_CAP_PROP_POS_AVI_RATIO": cv.CV_CAP_PROP_POS_AVI_RATIO,
    "CV_CAP_PROP_FRAME_WIDTH": cv.CV_CAP_PROP_FRAME_WIDTH,
    "CV_CAP_PROP_FRAME_HEIGHT": cv.CV_CAP_PROP_FRAME_HEIGHT,
    "CV_CAP_PROP_FPS": cv.CV_CAP_PROP_FPS,
    "CV_CAP_PROP_FOURCC": cv.CV_CAP_PROP_FOURCC,
    "CV_CAP_PROP_FRAME_COUNT": cv.CV_CAP_PROP_FRAME_COUNT,
    "CV_CAP_PROP_FORMAT": cv.CV_CAP_PROP_FORMAT,
    "CV_CAP_PROP_MODE": cv.CV_CAP_PROP_MODE,
    "CV_CAP_PROP_BRIGHTNESS": cv.CV_CAP_PROP_BRIGHTNESS,
    "CV_CAP_PROP_CONTRAST": cv.CV_CAP_PROP_CONTRAST,
    "CV_CAP_PROP_SATURATION": cv.CV_CAP_PROP_SATURATION,
    "CV_CAP_PROP_HUE": cv.CV_CAP_PROP_HUE,
    "CV_CAP_PROP_GAIN": cv.CV_CAP_PROP_GAIN,
    "CV_CAP_PROP_EXPOSURE": cv.CV_CAP_PROP_EXPOSURE,
    "CV_CAP_PROP_CONVERT_RGB": cv.CV_CAP_PROP_CONVERT_RGB,
    # "CV_CAP_PROP_WHITE_BALANCE_U": cv.CV_CAP_PROP_WHITE_BALANCE_U,
    # "CV_CAP_PROP_WHITE_BALANCE_V": cv.CV_CAP_PROP_WHITE_BALANCE_V,
    "CV_CAP_PROP_RECTIFICATION": cv.CV_CAP_PROP_RECTIFICATION,
    # "CV_CAP_PROP_ISO_SPEED": cv.CV_CAP_PROP_ISO_SPEED,
    # "CV_CAP_PROP_BUFFERSIZE ": cv.CV_CAP_PROP_BUFFERSIZE,
}
def show_data():
    for (key, value) in video_properties.items():
        print("{} = {}".format(key, cap.get(value)))

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)

    # Display the resulting frame
    cv2.imshow('frame', small)
    show_data()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
