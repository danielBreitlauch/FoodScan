from urllib2 import quote
from requests import get
from bs4 import BeautifulSoup

from FoodScan.BarcodeDescriptors.barcodeDescriptor import BarcodeDescriptor
from FoodScan.item import *
from pysimplelog import Logger


class CodeCheck(BarcodeDescriptor):

    def __init__(self):
        BarcodeDescriptor.__init__(self)
        self.logger = Logger('Codechecker')

    @staticmethod
    def url(barcode):
        base_url = 'http://www.codecheck.info/product.search'
        return '{0}?q={1}&OK=Suchen'.format(base_url, quote(barcode.encode('utf-8')))

    def item(self, barcode):
        url = CodeCheck.url(barcode)
        try:
            blob = BeautifulSoup(get(url).text, "html.parser")
            if not blob.find("meta", property="og:title"):
                return None

            ratings, numeric = self.parse_ratings(blob)

            return Item(name=self.parse_name(blob),
                        sub_name=self.parse_sub_name(blob),
                        cc_price=self.parse_price(blob),
                        url=url,
                        ingredients=self.parse_ingredients(blob),
                        ratings=ratings,
                        num_rating=numeric)
        except Exception, e:
            self.logger.warn("Exception while searching for " + barcode + "\n" + str(e))
            return None

    def parse_name(self, blob):
        return blob.find("meta", property="og:title")['content']

    def parse_sub_name(self, blob):
        return blob.find('h3', {'class': 'page-title-subline'}).text

    def parse_ingredients(self, blob):
        return blob.find('span', {'class': 'rated-ingredients'}).text

    def parse_price(self, blob):
        r = blob.find('div', {'class': "area", 'id': "price-container"})
        r = r.find('div', {'class': "lighter-right"})
        if not r:
            return None

        r.span.clear()
        price = r.text.replace('EUR', '').strip()
        p = price.split(',')

        return int(p[0]) * 100 + int(p[1])

    def parse_ratings(self, blob):
        r = blob.find('div', {'class': "area spacing ingredient-rating"})
        if not r:
            return [], 0

        ratings = r.findAll('div', {'class': 'c c-2 rating-color'})
        rate = r.findAll('div', {'class': 'c c-3 rating-color'})
        numbers = r.findAll('div', {'class': 'rating-group-header'})

        rate_list = []
        agg = 0
        num = 0
        for i in range(len(ratings)):
            val = self.map_rating_class(numbers[i].get('class', [])[1])
            if val > 0:
                agg += val
                num += 1
                rate_list.append(ratings[i].text + ": " + rate[i].text)

        return rate_list, agg / num if num else 0

    def map_rating_class(self, clazz):
        num = int(clazz.replace('pr-rating-', '')) / 100
        if num in [1,8]:
            return 0
        else:
            return num
