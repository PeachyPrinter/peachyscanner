import cv2
import numpy as np
import time

a_val = int(200)
b_val = int(255)
c_val = int(0)
d_val = int(0)

c_mode = [cv2.CHAIN_APPROX_NONE, cv2.CHAIN_APPROX_SIMPLE, cv2. CHAIN_APPROX_TC89_L1, cv2.CHAIN_APPROX_TC89_KCOS]
r_mode = [cv2.RETR_EXTERNAL, cv2.RETR_LIST, cv2.RETR_CCOMP, cv2.RETR_TREE, cv2.RETR_FLOODFILL]

def new_var_a(a_int):
    global a_val
    a_val = int(a_int)
    print a_val

def new_var_b(b_int):
    global b_val
    b_val = int(b_int)
    print b_val

def new_var_c(value):
    global c_val
    c_val = int(value)
    print c_val

def new_var_d(value):
    global d_val
    d_val = int(value)
    print d_val


def sub(a, b):
        sub1 = a - b
        mask = a < b
        sub1[mask] = 0
        return sub1.astype('uint8')

def show_line(a, line_number=100):
    out = np.zeros((256, a.shape[1], 3), dtype='uint8')
    line = a[line_number]
    for pos in range(line.shape[0]):
        val = line[pos]
        color = (int(val), int(0), int(255 - val))
        out = cv2.line(out, (pos, 255), (pos, 255 - val), color)
    return out

spf = [1]
source = cv2.imread('g.png')
cv2.imshow('Master', source)
cv2.createTrackbar('min', 'Master', 30, 255, new_var_a)
# cv2.createTrackbar('max', 'Master', 126, 255, new_var_b)
# cv2.createTrackbar('cmode', 'Master', 0, 3, new_var_b)
# cv2.createTrackbar('rmode', 'Master', 0, 4, new_var_b)
itera = 350
dia_x = 7
dia_y = 7
_video_capture = cv2.VideoCapture(0)
_video_capture.read()
while True:
    start_fps = time.time()
    # itera = itera + 0.3
    (retVal, source) = _video_capture.read()
    if retVal:
        img = source.copy()

        start = time.time()
        b, g, r = cv2.split(img)
        # ab, ag, ar = np.average(b), np.average(g), np.average(r)
        # b = sub(b, ab)
        # g = sub(g, ag)
        # r = sub(r, ar)
        # rel = sub(r, g)
        rel = (r * (255.0 / np.max(r))).astype('uint8')
        thresh = np.zeros(rel.shape, dtype='uint8')
        thresh[rel > a_val] = rel[rel > a_val]

        # rel = thresh.copy()

        erosion = cv2.erode(thresh, np.ones((2, 2), dtype=np.uint8), iterations=1)
        dilation = cv2.dilate(erosion, np.ones((3, 10), dtype=np.uint8), iterations=1)
        dial = (thresh == dilation).astype(np.uint8) * 255
        dial = cv2.bitwise_and(dial, thresh)

        total = (time.time() - start) * 1000

        cv2.putText(img, "{: 5.2f} ms".format(total), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0))
        cv2.putText(img, "{: 5.2f} fps".format(float(len(spf)) / sum(spf)), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0))

        pos = int(itera) % img.shape[0]

        master_image = np.zeros((960, 1280,3), dtype='uint8')
        master_image[:480, 0:640, :] = img
        master_image[480:, 0:640, 0] = rel
        master_image[:480:, 640:, 1] = thresh
        master_image[480:, 640:, 2] = dial


        # cv2.imshow('frame4', show_line(rel, pos))
        # cv2.line(rel, (0, pos), (rel.shape[1], pos), 255, 1)
        # cv2.imshow('di', dilation)
        # cv2.imshow('Relitve Red', rel)
        # cv2.imshow('Threshold Red', thresh)
        cv2.imshow('Master', master_image)
        # cv2.imshow('Processed', dial)
        # cv2.imshow('Master', source)
        # cv2.createTrackbar('min', 'Master', 30, 255, new_var_a)

        key = cv2.waitKey(1) & 255
        if key == ord('q'):
            break
        if key == ord('w'):
            itera = itera - 1
        if key == ord('s'):
            itera = itera + 1
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

cv2.destroyAllWindows()
