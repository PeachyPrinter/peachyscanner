# Sharpness causes HALO around the object 


import cv2
import numpy as np
import time

cam_properties = {
"CAP_PROP_POS_MSEC" : cv2.CAP_PROP_POS_MSEC,
"CAP_PROP_POS_FRAMES" : cv2.CAP_PROP_POS_FRAMES,
"CAP_PROP_POS_AVI_RATIO" : cv2.CAP_PROP_POS_AVI_RATIO,
"CAP_PROP_FRAME_WIDTH" : cv2.CAP_PROP_FRAME_WIDTH,
"CAP_PROP_FRAME_HEIGHT" : cv2.CAP_PROP_FRAME_HEIGHT,
"CAP_PROP_FPS" : cv2.CAP_PROP_FPS,
"CAP_PROP_FOURCC" : cv2.CAP_PROP_FOURCC,
"CAP_PROP_FRAME_COUNT" : cv2.CAP_PROP_FRAME_COUNT,
"CAP_PROP_FORMAT" : cv2.CAP_PROP_FORMAT,
"CAP_PROP_MODE" : cv2.CAP_PROP_MODE,
"CAP_PROP_BRIGHTNESS" : cv2.CAP_PROP_BRIGHTNESS,
"CAP_PROP_CONTRAST" : cv2.CAP_PROP_CONTRAST,
"CAP_PROP_SATURATION" : cv2.CAP_PROP_SATURATION,
"CAP_PROP_HUE" : cv2.CAP_PROP_HUE,
"CAP_PROP_GAIN" : cv2.CAP_PROP_GAIN,
"CAP_PROP_EXPOSURE" : cv2.CAP_PROP_EXPOSURE,
"CAP_PROP_CONVERT_RGB" : cv2.CAP_PROP_CONVERT_RGB,
"CAP_PROP_WHITE_BALANCE_BLUE_U" : cv2.CAP_PROP_WHITE_BALANCE_BLUE_U,
"CAP_PROP_RECTIFICATION" : cv2.CAP_PROP_RECTIFICATION,
"CAP_PROP_MONOCHROME" : cv2.CAP_PROP_MONOCHROME,
"CAP_PROP_SHARPNESS" : cv2.CAP_PROP_SHARPNESS,
"CAP_PROP_AUTO_EXPOSURE" : cv2.CAP_PROP_AUTO_EXPOSURE,
"CAP_PROP_GAMMA" : cv2.CAP_PROP_GAMMA,
"CAP_PROP_TEMPERATURE" : cv2.CAP_PROP_TEMPERATURE,
"CAP_PROP_TRIGGER" : cv2.CAP_PROP_TRIGGER,
"CAP_PROP_TRIGGER_DELAY" : cv2.CAP_PROP_TRIGGER_DELAY,
"CAP_PROP_WHITE_BALANCE_RED_V" : cv2.CAP_PROP_WHITE_BALANCE_RED_V,
"CAP_PROP_ZOOM" : cv2.CAP_PROP_ZOOM,
"CAP_PROP_FOCUS" : cv2.CAP_PROP_FOCUS,
"CAP_PROP_GUID" : cv2.CAP_PROP_GUID,
"CAP_PROP_ISO_SPEED" : cv2.CAP_PROP_ISO_SPEED,
"CAP_PROP_BACKLIGHT" : cv2.CAP_PROP_BACKLIGHT,
"CAP_PROP_PAN" : cv2.CAP_PROP_PAN,
"CAP_PROP_TILT" : cv2.CAP_PROP_TILT,
"CAP_PROP_ROLL" : cv2.CAP_PROP_ROLL,
"CAP_PROP_IRIS" : cv2.CAP_PROP_IRIS,
"CAP_PROP_SETTINGS" : cv2.CAP_PROP_SETTINGS,
}

threshold_value = int(100)
sigma = int(33)
apertureSize = int(3)
image_pic = 0
contrast = float(2.0)
brightness = 0

c_mode = [cv2.CHAIN_APPROX_NONE, cv2.CHAIN_APPROX_SIMPLE, cv2. CHAIN_APPROX_TC89_L1, cv2.CHAIN_APPROX_TC89_KCOS]
r_mode = [cv2.RETR_EXTERNAL, cv2.RETR_LIST, cv2.RETR_CCOMP, cv2.RETR_TREE, cv2.RETR_FLOODFILL]


def new_threshold_value(a_int):
    global threshold_value
    threshold_value = int(a_int)


def new_sigma(value):
    global sigma
    sigma = value / 100.0


def new_apertureSize(value):
    global apertureSize
    apertureSize = value


def new_image(value):
    global image_pic
    image_pic = value


def new_brightness(value):
    global brightness
    brightness = value


def new_contrast(value):
    global contrast
    contrast = value / 100.0


def sub(a, b):
        sub1 = a - b
        mask = a < b
        sub1[mask] = 0
        return sub1.astype('uint8')

def new_fps(value):
    global _video_capture
    _video_capture.set(cv2.CAP_PROP_FPS, value)


# def show_line(a, line_number=100):
#     out = np.zeros((256, a.shape[1], 3), dtype='uint8')
#     line = a[line_number]
#     for pos in range(line.shape[0]):
#         val = line[pos]
#         color = (int(val), int(0), int(255 - val))
#         out = cv2.line(out, (pos, 255), (pos, 255 - val), color)
#     return out


spf = [1]
source = np.ones((1, 400, 3), dtype='uint8')
cv2.imshow('controls', source)
cv2.createTrackbar('threshold', 'controls', threshold_value, 255, new_threshold_value)
cv2.createTrackbar('sigma', 'controls', sigma, 100, new_sigma)
cv2.createTrackbar('apertureSize', 'controls', apertureSize, 100, new_apertureSize)
cv2.createTrackbar('image', 'controls', 0, 5, new_image)
cv2.createTrackbar('brigntness', 'controls', brightness, 255, new_brightness)
cv2.createTrackbar('contrast', 'controls', int(contrast * 100), 10000, new_contrast)


dia_x = 3
dia_y = 7
_video_capture = cv2.VideoCapture(0)
_video_capture.read()

data = ""
for (text, value) in cam_properties.items():
    val = _video_capture.get(value)
    if val == -1.0:
        print "{} is Not Supported".format(text)
    else:
        data += "{} is Supported and set to {}\n".format(text, val)
print data
while True:
    start_fps = time.time()
    (retVal, source) = _video_capture.read()
    if retVal:
        source_image = source.copy()


## Process Images
        start = time.time()
        b_source, g_source, r_source = cv2.split(source_image)
        ab, ag, ar = np.average(b_source), np.average(g_source), np.average(r_source)
        blue_above = sub(b_source, ab)
        green_above = sub(g_source, ag)
        red_above = sub(r_source, ar)
        relative_image = sub(red_above, green_above).astype('int32')
        relative_image = relative_image + brightness
        contrast_factor = (259 * (contrast + 255))/(255 * (259 - contrast))
        relative_image = (contrast_factor * (relative_image - 128)) + 128
        relative_image[np.where(relative_image < 0)] = 0
        relative_image[np.where(relative_image > 255)] = 255
        relative_image.astype('uint8')
        thresh = np.zeros(relative_image.shape, dtype='uint8')
        thresh[relative_image > threshold_value] = relative_image[relative_image > threshold_value]

        # relative_image = thresh.copy()

        erosion = cv2.erode(thresh, np.ones((2, 2), dtype=np.uint8), iterations=4)
        dilation = cv2.dilate(erosion, np.ones((dia_x, dia_y), dtype=np.uint8), iterations=4)
        dial = (thresh == dilation).astype(np.uint8) * 255
        dial = cv2.bitwise_and(dial, thresh)

        v = threshold_value
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edges = cv2.Canny(thresh, lower, upper, apertureSize)

        first = np.argmax(edges, axis=1)
        leading_edge = np.ones((480, 640), dtype='uint8')
        for i in range(480):
            leading_edge[i, first[i]] = 255
        leading_edge[:,0] = 0


        total = (time.time() - start) * 1000
        # pos = int(itera) % source_image.shape[0]


## PLACE AND LABEL SCREENS
        master_image = np.zeros((960, 1920, 3), dtype='uint8')
        master_image[:480, 0:640, :] = source_image
        cv2.putText(master_image, "Original".format(total), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 128, 0))
        cv2.putText(master_image, "{: 5.2f} ms".format(total), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 128, 0))
        cv2.putText(master_image, "{: 5.2f} fps".format(float(len(spf)) / sum(spf)), (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 128, 0))

        master_image[480:, 0:640, 0] = edges
        cv2.putText(master_image, "Edges", (0, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0))

        master_image[:480:, 640:1280, 1] = thresh
        cv2.putText(master_image, "Threshold", (640, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0))

        pic_list = [(red_above, "Red above average"), (green_above, "Green above average"), (blue_above, "Blue above average"), (r_source, "r_source"), (g_source, "g_source"), (b_source, "b_source")]
        (pict, text) = pic_list[image_pic]
        color = 0
        if text[0] == 'G':
            color = 1
        if text[0] == 'R':
            color = 2
        master_image[480:, 640:1280, color] = pict
        cv2.putText(master_image, text, (640, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0))

        master_image[:480:, 1280:, 1] = leading_edge
        cv2.putText(master_image, "Max Value", (1280, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0))

        master_image[480:, 1280:, 2] = relative_image
        cv2.putText(master_image, "Relitive", (1280, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0))

        cv2.imshow('Master', master_image)

## GET KEYBOARD INPUTS

        key = cv2.waitKey(1) & 255
        if key == ord('q'):
            break
        if key == ord('y'):
            dia_y = abs(dia_y + 1)
            print ("dialstion x,y: {},{}".format(dia_x, dia_y))
        if key == ord('h'):
            dia_y = abs(dia_y - 1)
            print ("dialstion x,y: {},{}".format(dia_x, dia_y))
        if key == ord('g'):
            dia_x = abs(dia_x - 1)
            print ("dialstion x,y: {},{}".format(dia_x, dia_y))
        if key == ord('j'):
            dia_x = abs(dia_x + 1)
            print ("dialstion x,y: {},{}".format(dia_x, dia_y))

        stop_fps = time.time() - start_fps
        spf.append(stop_fps)
        if len(spf) > 10:
            spf = spf[-10:]

## CLEAN UP
cv2.destroyAllWindows()
