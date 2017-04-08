from pysimplelog import Logger
from keyboard_alike import reader


class BarcodeReader:

    def __init__(self, vendor_id, product_id):
        self.logger = Logger('Barcode scan')
        self.reader = reader.Reader(vendor_id, product_id, 84, 16, should_reset=False)
        self.reader.initialize()

    def __del__(self):
        if self.reader:
            self.reader.disconnect()

    def scan(self):
        self.logger.info('Waiting for scanner data')
        return self.reader.read().strip()
