
import logging
import os
import sys
import time
import argparse

from api.capture import Capture

def setup_logging(args):

    peachy_logger = logging.getLogger('peachy')
    logfile = os.path.join(config.PEACHY_PATH, 'peachyscanner.log')
    if os.path.isfile(logfile):
        os.remove(logfile)
    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = getattr(logging, args.loglevel.upper(), "INFO")
    if not isinstance(logging_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    if True:
        peachy_logger = logging.getLogger('peachy')
        peachy_logger.propagate = False
        logFormatter = logging.Formatter(logging_format)

        fileHandler = logging.FileHandler(logfile)
        consoleHandler = logging.StreamHandler()

        fileHandler.setFormatter(logFormatter)
        consoleHandler.setFormatter(logFormatter)

        peachy_logger.addHandler(fileHandler)
        peachy_logger.addHandler(consoleHandler)

        peachy_logger.setLevel(logging_level)
    else:
        logging.basicConfig(filename=logfile, format=logging_format, level=logging_level)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Peachy Scanner")
    parser.add_argument('-l', '--log',     dest='loglevel', action='store',      required=False, default="WARNING", help="Enter the loglevel [DEBUG|INFO|WARNING|ERROR] default: WARNING")
    parser.add_argument('-t', '--console', dest='console',  action='store_true', required=False, help="Logs to console not file")
    parser.add_argument('-m', '--module', dest='mod',  action='store', required=False, help='Activate a module (use "list" to get a list of available modules).')
    args, unknown = parser.parse_known_args()

    path = os.path.dirname(os.path.realpath(__file__))

    import config

    if not os.path.exists(config.PEACHY_PATH):
        os.makedirs(config.PEACHY_PATH)
    setup_logging(args)

    sys.argv = [sys.argv[0]]
    if args.mod:
        sys.argv.append("-m")
        sys.argv.append(args.mod)

    capture = Capture()
    capture.start()
    from gui import PeachyScannerApp
    PeachyScannerApp(capture).run()
    capture.shutdown()
