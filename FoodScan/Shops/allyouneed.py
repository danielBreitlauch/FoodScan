# -*- coding: utf-8 -*-

import pickle
import time
import urllib2
import urlparse
from datetime import datetime

from bs4 import BeautifulSoup
from requests import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from FoodScan.Shops.shop import Shop
from FoodScan.item import ShopItem


def extract_price(dom_item):
    integer = dom_item.find('span', class_='integerPart')
    integer.span.clear()
    integer = int(integer.text.strip())
    decimal = int(dom_item.find('span', class_='decimalPart').text.strip())
    return integer * 100 + decimal


class AllYouNeed(Shop):

    search_url_prefix = 'https://www.allyouneedfresh.de/suchen?term='

    def __init__(self, email, password, cookie_file="ayn_cookies"):
        self.base_url = 'https://www.allyouneedfresh.de'
        self.basket_url = 'https://www.allyouneedfresh.de/warenkorbuebersicht'
        self.take_url = 'https://www.allyouneedfresh.de/responsive/pages/checkout1.jsf'

        self.take_page_view_state = None
        Shop.__init__(self, email, password, cookie_file)
        self.driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
        # self.driver = webdriver.Chrome('./chromedriver')
        self.driver.set_window_size(1280, 1024)

    @staticmethod
    def search_url(name):
        return AllYouNeed.search_url_prefix + urllib2.quote(name.encode('utf-8'))

    def j_faces_view_state(self, url):
        res = self.session.get(url)
        blob = BeautifulSoup(res.text, "html.parser")
        return blob.find('input', {'name': 'javax.faces.ViewState'}).get('value')

    def login(self):
        print("Logging in...")
        self.session = Session()
        self.driver.get(self.base_url)
        time.sleep(1)
        self.driver.find_element_by_link_text("Anmelden").click()
        time.sleep(1)
        self.driver.find_element_by_id('zipCodeForm:loginEmail').send_keys(self.email)
        self.driver.find_element_by_id('zipCodeForm:loginPassword').send_keys(self.password)
        self.driver.find_element_by_id('zipCodeForm:loginButton').click()
        time.sleep(1)
        self.new_session_with_cookies(self.driver.get_cookies())
        self.take_page_view_state = self.j_faces_view_state(self.basket_url)
        self.save_session()

    def is_logged_in(self, html=None):
        if not html:
            html = self.session.get(self.base_url).text
        x = html.find('Anmelden/Registrieren')
        return x < 0

    def save_session(self):
        with open(self.cookie_file, 'w') as f:
            pickle.dump(self.driver.get_cookies(), f)

    def load_session(self):
        try:
            with open(self.cookie_file) as f:
                cookies = pickle.load(f)
                self.new_session_with_cookies(cookies)
                for cookie in cookies:
                    for k in ('name', 'value', 'domain', 'path', 'expiry'):
                        if k not in list(cookie.keys()):
                            if k == 'expiry':
                                cookie[k] = 1475825481
                    self.driver.add_cookie({k: cookie[k] for k in ('name', 'value', 'domain', 'path', 'expiry') if k in cookie})
                return self.is_logged_in()
        except IOError:
            return False

    def cart(self):
        html = self.session.get(self.basket_url).text
        x = html.find('Sie haben leider')
        if x > 0:
            return []

        blob = BeautifulSoup(html, "html.parser")
        r = blob.find('div', {'class': "panel-body table"})
        amount_col = r.findAll('span', {'class': 'td col-sm-1 nopadding text-nowrap text-center'})
        name_col = r.findAll('span', {'class': 'td col-sm-7 nopadding'})
        price_col = []
        for p in r.findAll('span', class_='td col-sm-3 text-center nopadding'):
            pr = p.find('span', class_='styledPrice')
            if pr:
                price_col.append(pr)

        article_col = []
        for d in r.findAll('div', class_="row"):
            for clazz in d.get('class'):  # article_col[0] is the table header
                if 'artId' in clazz:
                    article_col.append(int(clazz[5:]))
                    break

        res = []
        for i in range(len(amount_col)):
            article_id = article_col[i]
            amount = int(amount_col[i].text.replace('x', '').strip())
            item = name_col[i]
            link = urlparse.urljoin(self.base_url, item.find('a')['href'])
            price = extract_price(price_col[i])

            item.span.clear()
            name = item.text.strip()
            res.append(ShopItem(article_id, amount, name, price, link))
        return res

    def search(self, name):
        html = self.session.get(AllYouNeed.search_url(name)).text
        blob = BeautifulSoup(html, "html.parser")
        r = blob.select('div.product-box.item')

        ids = []
        perfect = []
        for i in r:
            link = i.find('a', class_='article-link')['href']
            link = urlparse.urljoin(self.base_url, link)
            price = extract_price(i.find('span', class_='product-price'))

            desc = i.find('div', class_='product-description')
            details = desc.find('span', class_='product-story').find('span')

            if details:
                details.extract()

            desc = desc.text.strip().replace('\n', ', ')
            for c in i['class']:
                if 'artId' in c:
                    article_id = int(c[5:])
                    item = ShopItem(article_id, 1, desc, price, link)
                    ids.append(item)
                    match = True
                    for criteria in name.split():
                        if criteria.lower() not in desc.lower():
                            match = False
                            break
                    if match:
                        perfect.append(item)

                    break

        return perfect if perfect else ids

    def take(self, item):
        self.driver.get(AllYouNeed.search_url(item.name))
        time.sleep(2)

        ccc = self.driver.find_element_by_css_selector('.artId' + str(item.article_id))
        ccc = ccc.find_element_by_class_name('product-cart')
        inps = ccc.find_elements_by_tag_name('input')
        if len(inps) == 0 or not inps[0].is_displayed():
            print("taking..")
            ccc = ccc.find_element_by_tag_name('a')
            ccc.click()
            time.sleep(3)

            ccc = self.driver.find_element_by_css_selector('.artId' + str(item.article_id))
            ccc = ccc.find_element_by_class_name('product-cart')
            inp = ccc.find_element_by_tag_name('input')
        else:
            inp = inps[0]
        inp.click()
        # inp.send_keys(Keys.CONTROL, 'a')
        inp.send_keys(str(item.amount))
        inp.send_keys(Keys.ENTER)
        time.sleep(1)

    def shelf_life(self, item_link):
        html = self.session.get(item_link).text
        blob = BeautifulSoup(html, "html.parser")
        for desc in blob.findAll('div', class_='product-card'):
            for more in desc.findAll('div', class_='product-story'):
                for td in more.findAll('div', class_='td'):
                    date = td.find("strong").text.strip()
                    return datetime.strptime(date, '%d.%m.%Y')
        return datetime.max


