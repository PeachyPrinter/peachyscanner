import cv,cv2
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from peachyscanner import Mapper

colour = [0,0,250]
global threshold
global blue, green, red

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

def set_pos(img,y,x,brg):
    img.itemset((y,x,0),brg[0])
    img.itemset((y,x,1),brg[1])
    img.itemset((y,x,2),brg[2])

def show_points(img):
    global red
    b,g,r = cv2.split(img)
    bc,gc,rc = b.copy(),g.copy(),r.copy()
    global threshold
    cv2.inRange(b,blue - threshold, blue + threshold,bc)
    cv2.inRange(g,green - threshold, green + threshold,gc)
    cv2.inRange(r,red - threshold, red + threshold,rc)
    # actual = [0 for i in range(img.shape[0])]
    # ypos = 0
    # for value in actual:
    #     if (value != -1):
    #         set_pos(altered,ypos,value,[0,255,0])
    #         set_pos(altered,ypos,value + 1,[0,255,0])
    #         set_pos(altered,ypos,value + 2,[0,255,0])
    #     ypos = ypos + 1
    return cv2.merge((bc,gc,rc))

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cv2.imshow('frame', frame)
cv.CreateTrackbar('threshold', 'frame', 20, 255, set_threshold)
cv.CreateTrackbar('blue', 'frame', 200, 255, set_blue)
cv.CreateTrackbar('green', 'frame', 200, 255, set_green)
cv.CreateTrackbar('red', 'frame', 200, 255, set_red)

cnt = 0 
while(True):
    cnt = cnt + 1
    work_begin = cv2.getTickCount()
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',show_points(frame))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    delta = cv2.getTickCount() - work_begin
    f = cv2.getTickFrequency()
    if cnt % 30 == 0:
        print('fps: %f' % (f / delta)) 

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()