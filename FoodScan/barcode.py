import struct
import select
import thread
import traceback

from pysimplelog import Logger


class Barcode:

    def __init__(self, device, callback):
        self.file = open(device, 'rb')
        self.callback = callback
        self.logger = Logger('Barcode scan')
        thread.start_new_thread(self.listen, ())

    def listen(self):
        while True:
            try:
                self.callback(self.scan())
            except Exception:
                traceback.print_exc()

    def scan(self):
        self.logger.info('Waiting for scanner data')

        # Wait for binary data from the scanner and then read it
        scan_complete = False
        scanner_data = ''
        while True:
            rlist, _wlist, _elist = select.select([self.file], [], [], 0.1)
            if rlist != []:
                new_data = ''
                while not new_data.endswith('\x01\x00\x1c\x00\x01\x00\x00\x00'):
                    new_data = rlist[0].read(16)
                    scanner_data += new_data
                # There are 4 more keystrokes sent after the one we matched against,
                # so we flush out that buffer before proceedin^g:
                [rlist[0].read(16) for i in range(4)]
                scan_complete = True
            if scan_complete:
                break

        # Parse the binary data as a barcode
        barcode = self.parse(scanner_data)
        self.logger.info("Scanned barcode '{0}'".format(barcode))
        return barcode

    @staticmethod
    def parse(scanner_data):
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

