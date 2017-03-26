from urllib2 import quote

from bs4 import BeautifulSoup
from pysimplelog import Logger
from requests import get

from FoodScan.BarcodeSync.BarcodeDecoder.barcodeDecoder import BarcodeDecoder
from FoodScan.items import *


class EanSearch(BarcodeDecoder):

    def __init__(self):
        BarcodeDecoder.__init__(self)
        self.logger = Logger('EanSearch')

    @staticmethod
    def url(barcode):
        return 'https://www.ean-search.org/perl/ean-search.pl?q=' + quote(barcode.encode('utf-8'))

    def item(self, barcode):
        url = EanSearch.url(barcode)
        try:
            blob = BeautifulSoup(get(url).text, "html.parser")
            if 'Excessive use' in blob.text:
                self.logger.warn("Overuse")
                return None

            name = blob.find('a', {'href': "/perl/ean-info.pl?ean=" + barcode})
            return Item(name=name.text,
                        url=url)
        except Exception, e:
            self.logger.warn("Exception while searching for " + barcode + "\n" + str(e))
            return None
