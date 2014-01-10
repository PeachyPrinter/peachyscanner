#!/usr/bin/env python

import cv
import cv2.cv as cv
import time
import random
import os
os.system('cls' if os.name=='nt' else 'clear')

MOUSE_MOVE  = 0;
MOUSE_DOWN  = 1;
MOUSE_UP    = 4;

class ColorPicker:
    """ simple colorpicker to see HSV values from openCV """
    _imageRGB = None;
    _imageHSV = None;

    def __init__( self ):
        cv.NamedWindow( "ColorPicker", 1 );
        cv.SetMouseCallback( "ColorPicker", self.onMouse );

        self._imageRGB = cv.LoadImage( "scanner/frames/0557.jpg" ); # "scanner/frames/0557.jpg" "scanner/test2.jpg"
        self._imageHSV = cv.CreateImage( cv.GetSize( self._imageRGB ), 8, 3 );
        #self.choice = choice
        #choice = (0,0,0)
        cv.CvtColor( self._imageRGB, self._imageHSV, cv.CV_BGR2HSV );
        cv.ShowImage( "ColorPicker", self._imageRGB );
        self.choice = (0,0,0)
        print( "Keys:\n"
            "    ESC - quit the program\n"
            "    b - switch to/from backprojection view\n"
            "To initialize tracking, drag across the object with the mouse\n" )

    def onMouse( self, event, mouseX, mouseY, flags, param ):
        if( event == MOUSE_DOWN ):
            pix = self._imageRGB[mouseY, mouseX];
            self.choice = pix
            print "X, Y >> H, S, V:", [mouseX, mouseY], pix;

#            print self._colorImage[100, 100]

    def run( self ):
        #


##########################################################33
        cv.NamedWindow("camera", 1)
        capture = cv.CaptureFromCAM(0)
        i = 0
        pan = 0 
        #color to detect bgr
        R = 40
        G = 104
        B = 220
        #amout grid size of points checked in image
        skip_x = 4
        skip_y = 4
        real_time = True
        # factor scales the size of the object in output.obj
        factor_y = .01
        factor_x = .01

        #user questions 
        answer = raw_input('live real time capture? y or n')
        if answer == 'n':
            real_time = False



        file = open('scanner/output.obj', 'w')
        file.write('o PeachyScan\n')
        
        if not real_time:
            
            path = 'scanner/frames/';
            # getting the list of files
            files = os.listdir(path);
            print(files)


        def color_dif(r,g,b,R,G,B):
            r_dif = abs(r - R)
            g_dif = abs(g - G)
            b_dif = abs(b - B)
            return(r_dif + g_dif + b_dif)

        def add_key(img, r,g,b,size=20):
            for rows in range(size):
                for colums in range(size):
                    img[colums,rows] = (b,g,r)
            return(img)

       









#######################################################################3

        self.choice = (0,0,0)
        while True:
            #


##########################################################33

            i += 1 
            pan += .01
            #print(i)
            #time.sleep(1)
            if real_time: 
                img = cv.QueryFrame(capture)
            

                cv.SaveImage('scanner/test2.jpg', img)
                mat = cv.LoadImageM('scanner/test2.jpg', cv.CV_LOAD_IMAGE_COLOR)
            #mat = cv.LoadImageM('scanner/edit.jpg', cv.CV_LOAD_IMAGE_COLOR)
            
            if not real_time:
                if i > 165 : 
                    i = 0
                file_name = '0' + str(557 + i ) + '.jpg'

                mat = cv.LoadImageM(path+file_name, cv.CV_LOAD_IMAGE_COLOR)
                #mat = cv.LoadImageM(path+files[i], cv.CV_LOAD_IMAGE_COLOR)

            
                

            #os.system('cls' if os.name=='nt' else 'clear')
            print(mat.rows)
            B,G,R = self.choice
            for row_number in range(mat.rows):
                if row_number % skip_y == 0 : 
                    pixle_row = []

                    for colum_number in range(mat.cols):
                        if colum_number % skip_x == 0:
                            rgb = mat[row_number,colum_number]
                            b, g, r = rgb
                            color_dif(r,g,b,R,G,B)
                            
                            pixle_row.append(color_dif(r,g,b,R,G,B))
                    #print(max(pixle_row))
                    
                    closest_yet = 20000
                    position = 0
                    bright_position = 0
                    for pixle_value in pixle_row:
                        position += skip_x

                        if pixle_value < closest_yet:
                            closest_yet = pixle_value
                            bright_position = position
                    #print(bright_position, ('*' * int(bright_position/20)) )
                    mat[row_number-skip_y, bright_position-skip_y] = (0,250,0)
                    file.write('v ' + str(row_number * factor_y) + ' ' + str(bright_position * factor_x) + ' ' + str(pan + (random.random()*.01))  +  '\n')
            mat = add_key(mat,R,G,B,20)
            cv.ShowImage("camera", mat)












#######################################################################3








            print(self.choice)
            c = cv.WaitKey(10)
            if c == 27:
                break
#//colorPicker

if __name__=="__main__":
    demo = ColorPicker()
    demo.run()
