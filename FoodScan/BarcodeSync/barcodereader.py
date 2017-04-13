import select
import struct
import traceback
from pysimplelog import Logger
import Queue
from thread import start_new_thread


class BarcodeReader:

    def __init__(self, device):
        self.logger = Logger('Barcode scan')
        self.file = open(device, 'rb')
        self.q = Queue.Queue()
        start_new_thread(self.scan, ())

    def scan(self):
        while True:
            try:
                self.logger.info('Waiting for scanner data')

                scanner_data = self.read()
                barcodes = self.parse(scanner_data).split()
                for barcode in barcodes:
                    self.logger.info("Scanned barcode '{0}'".format(barcode))
                    self.q.put(barcode)
            except Exception:
                traceback.print_exc()

    def read(self):
        # Wait for binary data from the scanner and then read it
        scanner_data = ''
        while True:
            read_list, _, _ = select.select([self.file], [], [], 0.1)
            if read_list:
                fd = read_list[0]

                new_data = ''
                while not new_data.endswith('\x01\x00\x1c\x00\x01\x00\x00\x00'):
                    new_data = fd.read(16)
                    scanner_data += new_data
                # There are 4 more keystrokes sent after the one we matched against,
                # so we flush out that buffer before proceeding:
                [fd.read(16) for _ in range(4)]
                return scanner_data

    @staticmethod
    def parse(scanner_data):
        # Parse the binary data as a barcode
        upc_chars = []
        for i in range(0, len(scanner_data), 16):
            chunk = scanner_data[i:i + 16]

            # The chunks we care about will match
            # __  __  __  __  __  __  __  __  01  00  __  00  00  00  00  00
            if chunk[8:10] != '\x01\x00' or chunk[11:] != '\x00\x00\x00\x00\x00':
                continue

            digit_int = struct.unpack('>h', chunk[9:11])[0]
            upc_chars.append(str((digit_int - 1) % 10))

        return ''.join(upc_chars)
