from FoodScan.BarcodeDescriptors.barcodeDescriptor import BarcodeDescriptor
from FoodScan.BarcodeDescriptors.codecheck import CodeCheck
from FoodScan.BarcodeDescriptors.digitEye import DigitEye
from FoodScan.BarcodeDescriptors.eanSearch import EanSearch
from FoodScan.BarcodeDescriptors.geizhalz import Geizhals


class BarcodeDescriptorCombiner(BarcodeDescriptor):

    def __init__(self):
        BarcodeDescriptor.__init__(self)
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
