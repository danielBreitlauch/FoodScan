# -*- coding: utf-8 -*-

import unicodedata
import pickle
import time
import urlparse
import re
from urllib2 import quote

from bs4 import BeautifulSoup
from pysimplelog import Logger
from requests import Session

from FoodScan.ShopSync.Shops.shop import Shop
from FoodScan.items import ShopItem


class Kaufland(Shop):

    search_url_prefix = 'https://shop.kaufland.de/search?pageSize=48&sort=relevance&text='

    def __init__(self, email, password, captcha_service, cookie_file="kl_cookies"):
        self.logger = Logger('Kaufland')
        self.captcha_service = captcha_service
        self.base_url = 'https://shop.kaufland.de'
        self.login_url = "https://shop.kaufland.de/login"
        self.account_url = "https://shop.kaufland.de/my-account"
        self.take_url = 'https://shop.kaufland.de/cart/modify'
        self.basket_url = 'https://shop.kaufland.de/cart'

        Shop.__init__(self, email, password, cookie_file)

    @staticmethod
    def search_url(name):
        return Kaufland.search_url_prefix + quote(name.encode('utf-8'))

    def login(self):
        self.logger.info("Logging in...")
        self.session = Session()
        html = self.session.get(self.account_url).text
        blob = BeautifulSoup(html, "html.parser")
        token = blob.find('input', {'name': 'CSRFToken'}).get('value')
        site_key = blob.find('input', {'id': 'siteKey'}).get('value')

        job = self.captcha_service.create(self.login_url, site_key)
        time.sleep(5)

        data = [
            ('j_username', self.email),
            ('j_password', self.password),
            ('g-recaptcha-response', self.captcha_service.result(job)),
            ('siteKeyCaptcha', site_key),
            ('submit-form', ''),
            ('CSRFToken', token),
        ]

        self.session.post(self.base_url + '/j_spring_security_check', data=data)
        self.save_session()

    def is_logged_in(self, html=None):
        if not html:
            html = self.session.get(self.account_url).text
        return html.find('Abmelden') > 0

    def save_session(self):
        with open(self.cookie_file, 'w') as f:
            pickle.dump(self.session.cookies, f)

    def load_session(self):
        try:
            with open(self.cookie_file) as f:
                cookies = pickle.load(f)
                self.session = Session()
                self.session.cookies = cookies
                return self.is_logged_in()
        except IOError:
            return False

    def get(self, url):
        html = self.session.get(url).text
        if self.is_logged_in(html):
            self.save_session()
            return html

        self.login()
        html = self.session.get(url).text
        if self.is_logged_in(html):
            self.save_session()
            return html

        self.logger.error("Can not log in")
        exit(1)

    def cart(self):
        blob = BeautifulSoup(self.get(self.basket_url), "html.parser")
        r = blob.select('section.product-list')
        if len(r) == 0:
            return []

        r = r[0]
        ids = []
        for i in r.findAll('article'):
            a = i.find('a')
            link = urlparse.urljoin(self.base_url, a['href'])
            title = i.find('p', {'class': 'product-list__title'}).text.strip()
            amount = i.find('div', {'class': 'product-list__amount'})
            article_id = amount['data-dynamicblock']
            amount = int(amount.find('input', {'name': 'quantity'}).get('value'))
            price = i.find('div', {'data-dynamiccontent': 'prices'})
            red = price.find('span', {'class': 'product-list__reduced-price'})
            if red:
                price = red
            price = price.text.replace(u'€', u'').strip()
            price = int(float(price) * 100)

            title = unicodedata.normalize('NFKC', title)

            item = ShopItem(article_id, amount, title, price, link)
            ids.append(item)

        return ids

    def search(self, term, sub_term=None):
        html = self.get(Kaufland.search_url(term))
        ids = self.parse_search(html)

        split_terms = [x for x in re.split('-| |\n', term) if len(x) > 1]

        if 0 < len(ids) < 48:
            return self.order_by_matches(split_terms, ids)

        if sub_term and len(ids) == 0:
            return self.search(term + " " + sub_term)

        if len(split_terms) > 1:
            ids = []
            for criteria in split_terms:
                if len(criteria) > 1:
                    ids += self.search(criteria)

        return self.order_by_matches(split_terms, ids, max=20, perfect=0.6, cut_off=0.25)

    def parse_search(self, html):
        blob = BeautifulSoup(html, "html.parser")
        ids = []
        r = blob.select('div.productmatrix')
        if len(r) > 0:
            r = r[0]
            for i in r.findAll('article'):
                a = i.find('a')
                article_id = i['data-dynamicblock'].split('_')[0]
                link = urlparse.urljoin(self.base_url, a['href'])
                title = a.find('p', {'class': 'product-tile__infos--title'}).text.strip()
                price = a.find('div', {'class': 'product-tile__price--regular'})
                if not price:
                    price = a.find('div', {'class': 'product-tile__price--reduced'})
                price = price.text.replace(u'€', u'').strip()
                price = int(float(price) * 100)

                title = unicodedata.normalize('NFKC', title)

                item = ShopItem(article_id, 1, title, price, link)
                ids.append(item)
        return ids

    def order_by_matches(self, terms, ids, max=None, perfect=None, cut_off=None):
        if len(ids) == 0:
            return []
        normal_fit = {}
        perfect_fit = {}
        normal_ids = []
        perfect_ids = []
        for item in ids:
            if item in normal_ids or item in perfect_ids:
                continue
            match = len([x for x in terms if x.lower() in item.name.lower()])
            if not cut_off or match > len(terms) * cut_off:
                normal_ids.append(item)
                normal_fit[item] = match
            if perfect and match > len(terms) * perfect:
                perfect_ids.append(item)
                perfect_fit[item] = match

        if len(perfect_fit) > 0:
            normal_ids = perfect_ids
            normal_fit = perfect_fit

        ordered = sorted(normal_ids, key=normal_fit.__getitem__, reverse=True)
        if max:
            ordered = ordered[:max]
        return ordered

    def take(self, item):
        html = self.get(Kaufland.search_url(item.name))
        blob = BeautifulSoup(html, "html.parser")
        token = blob.find('input', {'name': 'CSRFToken'}).get('value')

        self.session.post(self.take_url, data=[
            ('qty', item.amount),
            ('productCodePost', item.article_id),
            ('pageTemplate', 'producttile'),
            ('CSRFToken', token),
        ])
        self.save_session()

    def shelf_life(self, item_link):
        pass


