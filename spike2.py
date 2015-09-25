import pygame
import pygame.camera
from pygame.locals import *
import os


class Capture(object):
    def __init__(self):
        self.focus = 100
        self.size = (640, 480)
        self.display = pygame.display.set_mode(self.size, 0)

        pygame.init()
        pygame.camera.init()
        os.system('''uvcdynctrl  --set='Focus, Auto' 0''')
        os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))

        self.clist = pygame.camera.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        self.cam = pygame.camera.Camera(self.clist[0], self.size)
        self.cam.start()

        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

    def get_and_flip(self):
        if self.cam.query_image():
            self.snapshot = self.cam.get_image(self.snapshot)
        self.display.blit(self.snapshot, (0, 0))
        pygame.display.flip()

    def main(self):
        
        going = True
        while going:
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    self.cam.stop()
                    going = False
                if (e.type == KEYDOWN and e.key == K_w):
                    self.focus += 10
                    os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))
                    print('FOCUS: {}'.format(self.focus))
                if (e.type == KEYDOWN and e.key == K_s):
                    self.focus -= 10
                    os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))
                    print('FOCUS: {}'.format(self.focus))
            self.get_and_flip()

if __name__ == '__main__':
    Capture().main()