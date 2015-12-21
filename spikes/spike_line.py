import cv2
import numpy as np

a_val = int(30)
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


source = cv2.imread('g.png')
cv2.imshow('frame1', source)
cv2.createTrackbar('min', 'frame1', 30, 255, new_var_a)
# cv2.createTrackbar('max', 'frame1', 126, 255, new_var_b)
# cv2.createTrackbar('cmode', 'frame1', 0, 3, new_var_b)
# cv2.createTrackbar('rmode', 'frame1', 0, 4, new_var_b)
itera = 350
dia_x = 7
dia_y = 7
_video_capture = cv2.VideoCapture(0)
_video_capture.read()
while True:
    # itera = itera + 0.3
    (retVal, source) = _video_capture.read()
    if retVal:
        img = source.copy()
        b, g, r = cv2.split( img)
        ab, ag, ar = np.average(b), np.average(g), np.average(r)
        b = sub(b, ab)
        g = sub(g, ag)
        r = sub(r, ar)
        rel = sub(r, g)
        rel = (rel * (255.0 / np.max(rel))).astype('uint8')


        thresh = np.zeros(rel.shape, dtype='uint8')
        thresh[rel > 30] = rel[rel > 30]
        rel = thresh.copy()

        erosion = cv2.erode(rel, np.ones((2, 2), dtype=np.uint8), iterations=1)
        dilation = cv2.dilate(erosion, np.ones((3, 10), dtype=np.uint8), iterations=1)
        dial = (rel == dilation).astype(np.uint8) * 255
        dial = cv2.bitwise_and(dial, rel)


        pos = int(itera) % img.shape[0]
        cv2.imshow('frame4', show_line(rel, pos))
        cv2.line(rel, (0, pos), (rel.shape[1], pos), 255, 1)
        cv2.imshow('di', dilation)
        cv2.imshow('frame2', rel)
        cv2.imshow('frame1', img)

        cv2.imshow('dialate', cv2.resize(dial, (0, 0), fx=2.0, fy=2.0))
        cv2.imshow('frame1', source)
        cv2.createTrackbar('min', 'frame1', 30, 255, new_var_a)

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

cv2.destroyAllWindows()
