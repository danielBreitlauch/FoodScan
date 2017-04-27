import traceback

from FoodScan.BarcodeSync.BarcodeDecoder.barcodeDecoder import BarcodeDecoder
from FoodScan.BarcodeSync.BarcodeDecoder.codecheck import CodeCheck
from FoodScan.BarcodeSync.BarcodeDecoder.digitEye import DigitEye
from FoodScan.BarcodeSync.BarcodeDecoder.eanSearch import EanSearch
from FoodScan.BarcodeSync.BarcodeDecoder.geizhalz import Geizhals


class CascadingBarcodeDecoder(BarcodeDecoder):

    def __init__(self):
        BarcodeDecoder.__init__(self)
        self.cc = CodeCheck()
        self.es = EanSearch()
        self.de = DigitEye()
        self.gh = Geizhals()

    @staticmethod
    def url(barcode):
        return CodeCheck.url(barcode)

    def wrap(self, method, barcode):
        try:
            return method.item(barcode)
        except Exception:
            traceback.print_exc()
            return None

    def item(self, barcode):
        item = self.wrap(self.cc, barcode)
        if not item:
            item = self.wrap(self.gh, barcode)
        if not item:
            item = self.wrap(self.de, barcode)
        if not item:
            item = self.wrap(self.es, barcode)

        return item
