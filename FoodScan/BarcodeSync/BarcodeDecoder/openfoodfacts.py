# -*- coding: utf-8 -*-

from urllib.parse import quote
from pysimplelog import Logger
from openfoodfacts import API, Country

from FoodScan.BarcodeSync.BarcodeDecoder.barcodeDecoder import BarcodeDecoder
from FoodScan.items import *


class OpenFoodFacts(BarcodeDecoder):

    def __init__(self):
        BarcodeDecoder.__init__(self)
        self.logger = Logger('OpenFoodFacts')
        self.api = API(version="v2", country=Country.de)

    @staticmethod
    def url(barcode):
        return 'https://de.openfoodfacts.org/produkt/' + quote(barcode.encode('utf-8'))

    def item(self, barcode):
        try:
            answer = self.api.product.get(barcode)
            if answer['status_verbose'] != 'product found':
                return None
            
            return Item(name=answer['product']['product_name'],
                        sub_name=answer['product']['brands'],
                        url=OpenFoodFacts.url(barcode))
        except Exception as e:
            self.logger.warn("Exception while searching for " + barcode + "\n" + str(e))
            return None
