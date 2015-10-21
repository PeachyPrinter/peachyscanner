import threading

class VideoProcessor(threading.Thread):
    def __init__(self, camera, encoder):
        threading.Thread.__init__(self)
        self.camera = camera
        self.running = False
        self.handlers = []
        self.encoder = encoder

    def run(self):
        self.running = True
        while (self.running):
            for handler in self.handlers:
                frame = self.camera.read()
                should_capture, idx = self.encoder.should_capture_frame_at_index(frame)
                if should_capture:
                    handler.handle(frame=self.roi.get_left_of_center(frame))

    def stop(self):
        self.running = False
        self.join()

    def subscribe(self, handler):
        self.handlers.append(handler)