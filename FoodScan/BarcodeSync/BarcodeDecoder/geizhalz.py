# -*- coding: utf-8 -*-

from urllib2 import quote

from bs4 import BeautifulSoup
from pysimplelog import Logger
from requests import get

from FoodScan.BarcodeSync.BarcodeDecoder.barcodeDecoder import BarcodeDecoder
from FoodScan.items import *


class Geizhals(BarcodeDecoder):

    def __init__(self):
        BarcodeDecoder.__init__(self)
        self.logger = Logger('Geizhalz')

    @staticmethod
    def url(barcode):
        return 'https://geizhals.de/?fs=' + quote(barcode.encode('utf-8'))

    def item(self, barcode):
        url = Geizhals.url(barcode)
        try:
            blob = BeautifulSoup(get(url).text, "html.parser")
            blob = blob.find('div', {'id': 'gh_artbox'})
            if not blob:
                return None

            return Item(name=self.parse_name(blob),
                        price=self.parse_price(blob),
                        url=url)
        except Exception, e:
            self.logger.warn("Exception while searching for " + barcode + "\n" + str(e))
            return None

    def parse_name(self, blob):
        header = blob.find('h1', {'class': 'arthdr'})
        if header:
            return header.find('span', {'itemprop': 'name'}).text
        else:
            return blob.find('b', {'itemprop': 'name'}).next

    def parse_price(self, blob):
        header = blob.find('h1', {'class': 'arthdr'})
        if header:
            price = header.find('span', {'class': 'gh_price'})
            price = price.text.replace(u'€', '').strip()
            p = price.split(',')

            return int(p[0]) * 100 + int(p[1])
        else:
            return None
