from urllib2 import quote
from requests import get
from bs4 import BeautifulSoup
from item import *
from pysimplelog import Logger


class CodeCheck:

    base_url = 'http://www.codecheck.info/product.search'

    def __init__(self):
        self.logger = Logger('Codechecker')

    @staticmethod
    def url(term):
        return '{0}?q={1}&OK=Suchen'.format(CodeCheck.base_url, quote(term.encode('utf-8')))

    def get_description(self, term):
        url = CodeCheck.url(term)
        try:
            blob = BeautifulSoup(get(url).text, "html.parser")
            ratings, numeric = self.parse_ratings(blob)

            return Item(name=self.parse_name(blob),
                        cc_price=self.parse_price(blob),
                        cc_url=url,
                        ingredients=self.parse_ingredients(blob),
                        ratings=ratings,
                        num_rating=numeric)
        except Exception, e:
            self.logger.warn("Exception while searching for " + term + "\n" + str(e))

    def parse_name(self, blob):
        return blob.find("meta", property="og:title")['content']

    def parse_ingredients(self, blob):
        return blob.find('span', {'class': 'rated-ingredients'}).text

    def parse_price(self, blob):
        r = blob.find('div', {'class': "area", 'id': "price-container"})
        r = r.find('div', {'class': "lighter-right"})
        r.span.clear()
        price = r.text.replace('EUR', '').strip()
        p = price.split(',')

        return int(p[0]) * 100 + int(p[1])

    def parse_ratings(self, blob):
        r = blob.find('div', {'class': "area spacing ingredient-rating"})
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

        return rate_list, agg / num

    def map_rating_class(self, clazz):
        num = int(clazz.replace('pr-rating-', '')) / 100
        if num in [1,8]:
            return 0
        else:
            return num


from item import *
