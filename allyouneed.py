import pickle
import urllib2
import urlparse
from requests import *
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from datetime import datetime

from item import ShopItem


def extract_price(dom_item):
    integer = dom_item.find('span', class_='integerPart')
    integer.span.clear()
    integer = int(integer.text.strip())
    decimal = int(dom_item.find('span', class_='decimalPart').text.strip())
    return integer * 100 + decimal


class AllYouNeed:

    search_url_prefix = 'https://www.allyouneedfresh.de/suchen?term='

    def __init__(self):
        self.base_url = 'https://www.allyouneedfresh.de'
        self.basket_url = 'https://www.allyouneedfresh.de/warenkorbuebersicht'
        self.take_url = 'https://www.allyouneedfresh.de/responsive/pages/checkout1.jsf'

        self.session = Session()
        self.take_page_view_state = None

    @staticmethod
    def search_url(name):
        return AllYouNeed.search_url_prefix + urllib2.quote(name.encode('utf-8'))

    def set_cookies(self, email, passwd):
        driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
        driver.set_window_size(1280, 1024)
        driver.get(self.base_url)
        time.sleep(1)
        driver.find_element_by_link_text("Anmelden").click()
        time.sleep(1)
        driver.find_element_by_id('zipCodeForm:loginEmail').send_keys(email)
        driver.find_element_by_id('zipCodeForm:loginPassword').send_keys(passwd)
        driver.find_element_by_id('zipCodeForm:loginButton').click()
        time.sleep(1)
        cookie = driver.get_cookies()
        driver.quit()

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

    def j_faces_view_state(self, url):
        res = self.session.get(url)
        blob = BeautifulSoup(res.text, "html.parser")
        return blob.find('input', {'name': 'javax.faces.ViewState'}).get('value')

    def login(self, email, passwd):
        self.session = Session()
        self.set_cookies(email, passwd)
        self.take_page_view_state = self.j_faces_view_state(self.basket_url)

    def is_logged_in(self):
        html = self.session.get(self.base_url).text
        x = html.find('Anmelden/Registrieren')
        return x < 0

    def save_session(self, session_file):
        with open(session_file, 'w') as f:
            pickle.dump(self.session.cookies, f)

    def load_session(self, session_file):
        try:
            with open(session_file) as f:
                cookies = pickle.load(f)
                self.session = Session()
                self.session.cookies.update(cookies)
                return self.is_logged_in()
        except IOError:
            return False

    def load_session_or_log_in(self, session_file, email, password):
        if not self.load_session(session_file):
            print("Logging in...")
            self.login(email, password)
            self.save_session(session_file)

    def basket(self):
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

        article_col = r.findAll('div', class_="row")

        res = []
        for i in range(len(amount_col)):
            article_id = None
            for clazz in article_col[i + 1].get('class'): # article_col[0] is the table header
                if 'artId' in clazz:
                    article_id = int(clazz[5:])

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
        if perfect:
            return perfect
        else:
            return ids

    def take(self, item):
        data = {
            'searchForm': 'searchForm',
            'searchForm:searchInput': '',
            'javax.faces.ViewState': self.take_page_view_state,
            'javax.faces.source': 'j_idt386',
            'javax.faces.partial.execute': 'j_idt386 @component',
            'javax.faces.partial.render': '@component',
            'articleId': str(item.article_id),
            'amount': str(item.amount),
            'actionSource': 'REX_IMPULSE_PUCHASE_A_KU',
            'org.richfaces.ajax.component': 'j_idt386',
            'j_idt386': 'j_idt386',
            'rfExt': 'null',
            'AJAX:EVENTS_COUNT': '1',
            'javax.faces.partial.ajax': 'true'
        }

        answer = self.session.post(self.take_url, data=data).text
        if '<redirect url="/warenkorbuebersicht"></redirect></partial-response>' in answer:
            print("failure to take " + item.name)

    def increase(self, item):
        for i in self.basket():
            if i.article_id == item.article_id:
                item.amount += i.amount

        self.take(item)

    def delete(self, item):
        item.amount = 0
        self.take(item)

    def shelf_life(self, item_link):
        html = self.session.get(item_link).text
        blob = BeautifulSoup(html, "html.parser")
        for desc in blob.findAll('div', class_='product-card'):
            for more in desc.findAll('div', class_='product-story'):
                for td in more.findAll('div', class_='td'):
                    date = td.find("strong").text.strip()
                    return datetime.strptime(date, '%d.%m.%Y')
        return datetime.max


