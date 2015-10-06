import logging
import subprocess
from threading import Lock

logger = logging.getLogger('peachy')

class CameraControl(object):
    def __init__(self):
        self._lock = Lock()
        self._run_command('''uvcdynctrl  --set='Focus, Auto' 0''')
        self._run_command('''uvcdynctrl  --set='White Balance Temperature, Auto' 0''')
        self._run_command('''uvcdynctrl  --set='Focus (absolute)' 0''')
        self._run_command('''uvcdynctrl  --set='Focus (absolute)' 255''')
        self._focus = 0
        self._brightness = 0
        self._contrast = 0
        self._white_balance = 0
        self._sharpness = 0


    def _run_command(self, command):
        proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        (out, error) = proc.communicate()
        if error:
            raise Exception(error)
        else:
            return out

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, amount):
        self._focus = amount
        self._lock.acquire()
        self._run_command('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self._focus))
        logger.info('FOCUS: {}'.format(self._focus))
        self._lock.release()

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        self._brightness = brightness
        self._lock.acquire()
        self._run_command('''uvcdynctrl --set='Brightness' {}'''.format(self._brightness))
        logger.info('Brightness: {}'.format(self._brightness))
        self._lock.release()

    @property
    def contrast(self):
        return self._contrast

    @contrast.setter
    def contrast(self, contrast):
        self._contrast = contrast
        self._lock.acquire()
        self._run_command('''uvcdynctrl --set='Contrast' {}'''.format(self._contrast))
        logger.info('Contrast: {}'.format(self._contrast))
        self._lock.release()

    @property
    def white_balance(self):
        return self._white_balance

    @white_balance.setter
    def white_balance(self, white_balance):
        self._white_balance = white_balance
        self._lock.acquire()
        self._run_command('''uvcdynctrl --set='White Balance Temperature' {}'''.format(self._white_balance))
        logger.info('White_balance: {}'.format(self._white_balance))
        self._lock.release()

    @property
    def sharpness(self):
        return self._sharpness

    @sharpness.setter
    def sharpness(self, sharpness):
        self._sharpness = sharpness
        self._lock.acquire()
        self._run_command('''uvcdynctrl --set='Sharpness' {}'''.format(self._sharpness))
        logger.info('Sharpness: {}'.format(self._sharpness))
        self._lock.release()

