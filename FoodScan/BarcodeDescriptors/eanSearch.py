from urllib2 import quote
from requests import get
from bs4 import BeautifulSoup

from FoodScan.BarcodeDescriptors.barcodeDescriptor import BarcodeDescriptor
from FoodScan.item import *
from pysimplelog import Logger


class EanSearch(BarcodeDescriptor):

    def __init__(self):
        BarcodeDescriptor.__init__(self)
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
