import threading


class VideoProcessor(threading.Thread):
    def __init__(self, camera, encoder, roi):
        threading.Thread.__init__(self)
        self.camera = camera
        self.running = False
        self.handlers = []
        self.encoder = encoder
        self.roi = roi

    def run(self):
        self.running = True
        while (self.running):
            frame = self.camera.read()
            should_capture, section = self.encoder.should_capture_frame_for_section(frame)
            if should_capture:
                for handler in self.handlers:
                    roi = self.roi.get_left_of_center(frame)
                    if not handler.handle(frame=roi, section=section):
                        self.unsubscribe(handler)

    def stop(self):
        self.running = False
        self.join()

    def subscribe(self, handler):
        self.handlers.append(handler)

    def unsubscribe(self, handler):
        self.handlers.remove(handler)
