from urllib.parse import quote

from bs4 import BeautifulSoup
from pysimplelog import Logger
from requests import get

from FoodScan.BarcodeSync.BarcodeDecoder.barcodeDecoder import BarcodeDecoder
from FoodScan.items import *


class DigitEye(BarcodeDecoder):

    def __init__(self):
        BarcodeDecoder.__init__(self)
        self.logger = Logger('DigitEye')

    @staticmethod
    def url(barcode):
        return 'http://www.digit-eyes.com/cgi-bin/digiteyes.cgi?upcCode=' + quote(barcode.encode('utf-8'))

    def item(self, barcode):
        try:
            url = DigitEye.url(barcode)
            blob = BeautifulSoup(get(url).text, "html.parser")

            if 'Please log in to look up EAN and UPC codes' in blob.text:
                self.logger.warn("Overuse")
                return None

            if not blob.find('h2', {'id': "description"}):
                return None

            name = blob.find('h2', {'id': "description"}).text

            ingredients = ""
            if blob.find('td', {'id': "ingredients"}):
                ingredients = blob.find('td', {'id': "ingredients"}).text

            return Item(name=name,
                        url=url,
                        ingredients=ingredients)
        except Exception as e:
            self.logger.warn("Exception while searching for " + barcode + "\n" + str(e))
            return None
