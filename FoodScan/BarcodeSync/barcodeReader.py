import traceback
import evdev

from evdev import categorize
from pysimplelog import Logger
import queue
from _thread import start_new_thread


class BarcodeReader:

    def __init__(self, device):
        self.logger = Logger("Barcode scan")

        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for d in devices:
            if device in d.name:
                self.logger.info("Found device " + d.name)
                self.device = d
                break

        if self.device is None:
            raise Exception("No barcode device found")

        self.q = queue.Queue()
        start_new_thread(self.scan, ())

    def scan(self):
        while True:
            try:
                self.logger.info('Waiting for scanner data')
                barcode = self.read()
                self.logger.info("Scanned barcode '{0}'".format(barcode))
                self.q.put(barcode)
            except Exception:
                traceback.print_exc()

    def read(self):
        current_barcode = ""
        for event in self.device.read_loop():
            if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                keycode = categorize(event).keycode
                if keycode == 'KEY_ENTER':
                    return current_barcode
                else:
                    current_barcode += keycode[4:]
