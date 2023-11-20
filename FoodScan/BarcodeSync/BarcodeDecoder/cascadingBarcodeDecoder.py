from collections import OrderedDict
import traceback

from FoodScan.BarcodeSync.BarcodeDecoder.barcodeDecoder import BarcodeDecoder
from FoodScan.BarcodeSync.BarcodeDecoder.codecheck import CodeCheck
from FoodScan.BarcodeSync.BarcodeDecoder.digitEye import DigitEye
from FoodScan.BarcodeSync.BarcodeDecoder.eanSearch import EanSearch
from FoodScan.BarcodeSync.BarcodeDecoder.geizhalz import Geizhals
from FoodScan.BarcodeSync.BarcodeDecoder.openfoodfacts import OpenFoodFacts


class CascadingBarcodeDecoder(BarcodeDecoder):

    def __init__(self):
        BarcodeDecoder.__init__(self)
        self.methods = OrderedDict(OpenFoodFacts(), CodeCheck(), EanSearch(), DigitEye(), Geizhals())

    @staticmethod
    def url(barcode):
        return CodeCheck.url(barcode)

    def item(self, barcode):
        for method in self.methods:
            try:
                item = method.item(barcode)
                if item:
                    return item
            except Exception:
                traceback.print_exc()
                return None
            
        return None
