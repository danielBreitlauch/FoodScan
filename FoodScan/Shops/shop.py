# -*- coding: utf-8 -*-

import abc
from requests import Session


class Shop:

    def __init__(self, email, password, cookie_file):
        self.session = Session()
        self.email = email
        self.password = password
        self.cookie_file = cookie_file
        if not self.load_session():
            self.login()

    @staticmethod
    @abc.abstractmethod
    def search_url(name):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def login(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def is_logged_in(self, html=None):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def save_session(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def load_session(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def cart(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def search(self, term, sub_term=None):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def take(self, item):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def shelf_life(self, item_link):
        raise NotImplementedError('users must define __str__ to use this base class')

    def new_session_with_cookies(self, cookie):
        self.session = Session()
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

    def increase(self, item):
        for i in self.cart():
            if i.article_id == item.article_id:
                item.amount += i.amount

        self.take(item)

    def delete(self, item):
        item.amount = 0
        self.take(item)
