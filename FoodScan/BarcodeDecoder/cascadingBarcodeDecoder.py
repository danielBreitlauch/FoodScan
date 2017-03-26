from FoodScan.BarcodeDecoder.barcodeDecoder import BarcodeDecoder
from FoodScan.BarcodeDecoder.codecheck import CodeCheck
from FoodScan.BarcodeDecoder.digitEye import DigitEye
from FoodScan.BarcodeDecoder.eanSearch import EanSearch
from FoodScan.BarcodeDecoder.geizhalz import Geizhals


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

    def item(self, barcode):
        item = self.cc.item(barcode)
        if not item:
            item = self.gh.item(barcode)
        if not item:
            item = self.de.item(barcode)
        if not item:
            item = self.es.item(barcode)

        return item
