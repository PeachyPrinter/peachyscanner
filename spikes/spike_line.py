import cv2
import numpy as np

a_val = int(20)
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
        # out[255 - val, pos] = [val, 0, 255 - val]
    return out



source = cv2.imread('g.png')
cv2.imshow('frame1', source)
cv2.createTrackbar('min', 'frame1', 20, 255, new_var_a)
cv2.createTrackbar('max', 'frame1', 126, 255, new_var_b)
cv2.createTrackbar('cmode', 'frame1', 0, 3, new_var_b)
cv2.createTrackbar('rmode', 'frame1', 0, 4, new_var_b)
itera = 0
while True:
    # itera = itera + 0.3
    img = source.copy()
    b, g, r = cv2.split( img)
    ab, ag, ar = np.average(b), np.average(g), np.average(r)
    b = sub(b, ab)
    g = sub(g, ag)
    r = sub(r, ar)
    rel = sub(r, g)
    rel = (rel * (255.0 / np.max(rel))).astype('uint8')
    thresh = np.zeros(rel.shape, dtype='uint8')
    thresh[rel > a_val] = rel[rel > a_val]
    rel = thresh.copy()
    # im2, contours, hierarchy = cv2.findContours(thresh, r_mode[d_val], c_mode[c_val])
    # thresh = (thresh > a_val).astype('uint8') * 255
    # notthresh = np.invert(thresh)
    # img = cv2.bitwise_and(img, img, mask=notthresh)
    # blue = np.zeros(img.shape, dtype='uint8')
    # blue[:, :, 0] = 255
    # blues = cv2.bitwise_and(blue, blue, mask=thresh)
    # img = img + blues

    pos = int(itera) % img.shape[0]
    cv2.imshow('frame4', show_line(rel, pos))
    cv2.line(rel, (0, pos), (rel.shape[1], pos), 255, 1)
    # cv2.imshow('frame3', thresh)
    cv2.imshow('frame2', rel)
    cv2.imshow('frame1', img)
    # cv2.imshow('frame2', curves)

    key = cv2.waitKey(1) & 255
    if key == ord('q'):
        break
    if key == ord('w'):
        itera = itera - 1
    if key == ord('s'):
        itera = itera + 1

cv2.destroyAllWindows()
