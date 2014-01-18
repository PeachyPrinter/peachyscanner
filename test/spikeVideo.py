import cv,cv2
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from peachyscanner import Mapper
global colour
colour = [0,0,250]
global threshold
global blue, green, red
global frame

threshold = 50
blue,green,red = 200, 200, 200

def set_threshold(x):
    global threshold
    threshold = x

def set_red(x):
    global red
    red = x

def set_green(x):
    global green
    green = x

def set_blue(x):
    global blue
    blue = x

def mouse_click(event,x,y,flags,param):
    if event == 1:
        global frame,red,green,blue
        print('%d:%d' % (x,y))
        blue = frame.item(y,x,0)
        green = frame.item(y,x,1)
        red = frame.item(y,x,2)
        cv2.setTrackbarPos('red', 'frame', red)
        cv2.setTrackbarPos('green', 'frame', green)
        cv2.setTrackbarPos('blue', 'frame', blue)

def set_pos(img,y,x,brg):
    img.itemset((y,x,0),brg[0])
    img.itemset((y,x,1),brg[1])
    img.itemset((y,x,2),brg[2])

def getLower(value,threshold):
    lower = value - threshold
    if lower < 0:
        lower = 0
    return lower

def getUpper(value, threshold):
    upper = value + threshold
    if upper > 255:
        upper = 255
    return upper

def show_points(img):
    b,g,r = cv2.split(img)
    global threshold
    bc = cv2.inRange(b,getLower(blue,threshold), getUpper(blue,threshold))
    gc = cv2.inRange(g,getLower(green,threshold), getUpper(green,threshold))
    rc = cv2.inRange(r,getLower(red,threshold), getUpper(red,threshold))
    cv2.bitwise_and(bc,gc,bc)
    cv2.bitwise_and(bc,rc,rc)
    return rc

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cv2.imshow('frame', frame)
cv.CreateTrackbar('threshold', 'frame', 20, 40, set_threshold)
cv.CreateTrackbar('blue', 'frame', 128, 255, set_blue)
cv.CreateTrackbar('green', 'frame', 128, 255, set_green)
cv.CreateTrackbar('red', 'frame', 128, 255, set_red)
cv2.setMouseCallback('frame',mouse_click)

cnt = 0 
original = True
while(True):
    cnt = cnt + 1
    work_begin = cv2.getTickCount()
    ret, frame = cap.read()
    if original:
        cv2.imshow('frame',frame)
    else:
        cv2.imshow('frame',show_points(frame))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1) & 0xFF == ord('t'):
        original = not original
    delta = cv2.getTickCount() - work_begin
    f = cv2.getTickFrequency()
    if cnt % 30 == 0:
        print('fps: %f' % (f / delta)) 

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()