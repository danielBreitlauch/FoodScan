# -*- coding: utf-8 -*-

import pickle
import urllib2
import urlparse
from requests import *
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from item import ShopItem


class Kaufland:

    search_url_prefix = 'https://shop.kaufland.de/search/?text='

    def __init__(self, email, password):
        self.base_url = 'https://shop.kaufland.de'
        self.login_url = "https://shop.kaufland.de/login"
        self.account_url = "https://shop.kaufland.de/my-account"
        self.take_url = 'https://shop.kaufland.de/cart/modify'
        self.basket_url = 'https://shop.kaufland.de/cart'

        self.email = email
        self.password = password
        self.session = Session()
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.set_window_size(1280, 1030)

    @staticmethod
    def search_url(name):
        return Kaufland.search_url_prefix + urllib2.quote(name.encode('utf-8'))

    def cookies_to_session(self, cookie):
        for c in cookie:
            if 'expiry' in c:
                ex = c['expiry']
                c.pop('expiry')
                c['expires'] = ex
            if 'HttpOnly' in c:
                hto = c['HttpOnly']
                c.pop('HttpOnly')
                c['rest'] = {'HttpOnly': hto}
            if 'httpOnly' in c:
                hto = c['httpOnly']
                c.pop('httpOnly')
                c['rest'] = {'HttpOnly': hto}
            if 'httponly' in c:
                hto = c['httponly']
                c.pop('httponly')
                c['rest'] = {'HttpOnly': hto}
            self.session.cookies.set(**c)

    def set_cookies(self):
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
        self.cookies_to_session(self.driver.get_cookies())

    def login(self):
        print("Logging in...")
        self.session = Session()
        self.set_cookies()

    def is_logged_in(self):
        html = self.session.get(self.account_url).text
        x = html.find('Breitlauch')
        y = html.find('Abmelden')
        return x > 0 and y > 0

    def save_session(self, session_file):
        with open(session_file, 'w') as f:
            pickle.dump(self.driver.get_cookies(), f)

    def load_session(self, session_file):
        try:
            with open(session_file) as f:
                cookies = pickle.load(f)
                self.session = Session()
                self.cookies_to_session(cookies)
                return self.is_logged_in()
        except IOError:
            return False

    def load_session_or_log_in(self, session_file):
        if not self.load_session(session_file):
            self.login()
            self.save_session(session_file)

    def basket(self):
        html = self.session.get(self.basket_url).text
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
        blob = BeautifulSoup(html, "html.parser")
        r = blob.select('div.productmatrix')[0]

        ids = []
        perfect = []
        for i in r.findAll('article'):
            a = i.find('a')
            article_id = i['data-dynamicblock'].split('_')[0]
            link = urlparse.urljoin(self.base_url, a['href'])
            title = a.find('p', {'class': 'product-tile__infos--title'}).text.strip()
            price = a.find('div', {'class': 'product-tile__price--regular'}).text.replace(u'€', u'').strip()
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
        blob = BeautifulSoup(html, "html.parser")
        token = blob.find('input', {'name': 'CSRFToken'}).get('value')

        self.session.post(self.take_url, data=[
            ('qty', item.amount),
            ('productCodePost', item.article_id),
            ('pageTemplate', 'producttile'),
            ('CSRFToken', token),
        ])

    def increase(self, item):
        for i in self.basket():
            if i.article_id == item.article_id:
                item.amount += i.amount

        self.take(item)

    def delete(self, item):
        item.amount = 0
        self.take(item)

    def shelf_life(self, item_link):
        pass


