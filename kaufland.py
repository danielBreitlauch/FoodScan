# -*- coding: utf-8 -*-

import pickle
import urllib2
import urlparse
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from item import ShopItem
from shop import Shop


class Kaufland(Shop):

    search_url_prefix = 'https://shop.kaufland.de/search/?text='

    def __init__(self, email, password, cookie_file="kl_cookies"):
        self.base_url = 'https://shop.kaufland.de'
        self.login_url = "https://shop.kaufland.de/login"
        self.account_url = "https://shop.kaufland.de/my-account"
        self.take_url = 'https://shop.kaufland.de/cart/modify'
        self.basket_url = 'https://shop.kaufland.de/cart'

        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.set_window_size(1280, 1030)
        Shop.__init__(self, email, password, cookie_file)

    @staticmethod
    def search_url(name):
        return Kaufland.search_url_prefix + urllib2.quote(name.encode('utf-8'))

    def login(self):
        print("Logging in...")
        # self.session = Session()
        self.driver.get(self.login_url)
        time.sleep(1)

        self.driver.find_element_by_id('j_username').send_keys(self.email)
        self.driver.find_element_by_id('j_password').send_keys(self.password)
        subs = self.driver.find_elements_by_tag_name('button')
        for el in subs:
            if "Anmelden" in el.text:
                el.click()
                break

        time.sleep(1)
        self.new_session_with_cookies(self.driver.get_cookies())
        self.save_session()

    def is_logged_in(self, html=None):
        if not html:
            html = self.session.get(self.account_url).text
        x = html.find('Breitlauch')
        y = html.find('Abmelden')
        return x > 0 and y > 0

    def save_session(self):
        with open(self.cookie_file, 'w') as f:
            pickle.dump(self.driver.get_cookies(), f)

    def load_session(self):
        try:
            with open(self.cookie_file) as f:
                cookies = pickle.load(f)
                self.new_session_with_cookies(cookies)
                return self.is_logged_in()
        except IOError:
            return False

    def cart(self):
        html = self.session.get(self.basket_url).text
        if not self.is_logged_in(html):
            self.login()
            return self.cart()

        blob = BeautifulSoup(html, "html.parser")
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
            price = price.text.replace(u'€', u'').strip()
            price = int(float(price) * 100)

            item = ShopItem(article_id, amount, title, price, link)
            ids.append(item)

        return ids

    def search(self, term):
        html = self.session.get(Kaufland.search_url(term)).text
        if not self.is_logged_in(html):
            self.login()
            return self.search(term)

        blob = BeautifulSoup(html, "html.parser")
        r = blob.select('div.productmatrix')[0]

        ids = []
        perfect = []
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

            item = ShopItem(article_id, 1, title, price, link)
            ids.append(item)

            match = True
            for criteria in term.split():
                if criteria.lower() not in title.lower():
                    match = False
                    break
            if match:
                perfect.append(item)

        return perfect if perfect else ids

    def take(self, item):
        html = self.session.get(Kaufland.search_url(item.name)).text
        if not self.is_logged_in(html):
            self.login()
            return self.take(item)

        blob = BeautifulSoup(html, "html.parser")
        token = blob.find('input', {'name': 'CSRFToken'}).get('value')

        self.session.post(self.take_url, data=[
            ('qty', item.amount),
            ('productCodePost', item.article_id),
            ('pageTemplate', 'producttile'),
            ('CSRFToken', token),
        ])

    def shelf_life(self, item_link):
        pass


