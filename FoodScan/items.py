# -*- coding: utf-8 -*-
import abc


class SubItem:
    def __init__(self):
        pass

    @abc.abstractmethod
    def title(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def selected(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @classmethod
    @abc.abstractmethod
    def parse(cls, string):
        raise NotImplementedError('users must define __str__ to use this base class')


class ListItem:
    def __init__(self):
        pass

    @abc.abstractmethod
    def title(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def note(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def position(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def sub_items(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @classmethod
    @abc.abstractmethod
    def parse(cls, title, notes, sub_tasks):
        raise NotImplementedError('users must define __str__ to use this base class')


class ShopItem(SubItem):
    def __init__(self, article_id, amount, name, price, link, select=False):
        SubItem.__init__(self)
        self.article_id = article_id
        self.amount = amount
        self.name = name
        self.price = price
        self.link = link
        self.select = select

    def title(self):
        return str(self.price / 100.0) + '€ ' + self.name + ' (' + self.link + ')'

    def selected(self):
        return self.select

    def __eq__(self, other):
        return other and self.price == other.price and self.link == other.link

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        return hash(self.name)

    @classmethod
    def parse(cls, string):
        price_end = string.find('€ ')
        name_end = string.rfind(' (', price_end)
        link_end = string.find(')', name_end)

        price = int(float(string[:price_end]) * 100)
        name = string[price_end + 2:name_end]
        link = string[name_end + 2:link_end]

        return ShopItem(None, None, name, price, link)


class Item(ListItem):
    def __init__(self, name, sub_name=None, price=None, ingredients=None, ratings=None, url=None, amount=1, num_rating=0):
        ListItem.__init__(self)
        self.name = name
        self.sub_name = sub_name
        self.price = price
        self.ingredients = ingredients
        self.ratings_data = ratings
        self.num_rating = num_rating
        self.amount = amount
        self.shop_items = None
        self.selected_item = None
        if url:
            self.url = url
        else:
            from FoodScan.BarcodeSync.BarcodeDecoder.cascadingBarcodeDecoder import CascadingBarcodeDecoder
            self.url = CascadingBarcodeDecoder.url(self.name)

    def inc_amount(self, amount=1):
        self.amount += amount

    def set_shop_items(self, shop_items):
        self.shop_items = []
        selected_replaced = False
        for item in shop_items:
            item.amount = self.amount
            self.shop_items.append(item)

            if item == self.selected_item or item.selected():
                self.selected_item = item
                self.selected_item.select = True
                selected_replaced = True

        if self.selected_item and not selected_replaced:
            self.selected_item = None

    def select_shop_item(self, item):
        if self.shop_items is None and item is not None:
            self.shop_items = [item]

        if item is None:
            self.selected_item = None
        else:
            for i in self.shop_items:
                if i == item:
                    self.selected_item = i
                    self.selected_item.select = True
                    self.selected_item.amount = self.amount

    def selected_shop_item(self):
        if self.selected_item:
            self.selected_item.amount = self.amount
        return self.selected_item

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def synced(self):
        return self.selected_item is not None

    def searched(self):
        return self.shop_items is not None

    def title(self):
        title = ""
        price = self.price
        if self.synced():
            title = "\\u2713 "
            price = self.selected_item.price
        elif self.searched():
            title = "\\u2605 "

        title += str(self.amount) + " " + self.name

        if price and price > 0:
            title += " -=(" + str(price / 100.0) + '€)'

        return title

    def note(self):
        note = ''

        if self.sub_name:
            note += self.sub_name + '\n\n'

        note += '* ' + self.url + '\n\n'

        if self.ratings_data:
            for rating in self.ratings_data:
                note += '* ' + rating + '\n'

        if self.ingredients:
            note += '\nInhalt:\n' + self.ingredients

        return note

    def position(self):
        return None

    def sub_items(self):
        if self.shop_items:
            return self.shop_items
        else:
            return []

    @classmethod
    def parse(cls, title, notes, sub_tasks):
        name, amount, price, num_rating = cls.parse_title(title)
        cc_url, ingredients, ratings, sub_name = cls.parse_notes(notes)
        shop_items = cls.parse_subs(sub_tasks)

        item = Item(name=name,
                    sub_name=sub_name,
                    ingredients=ingredients,
                    url=cc_url,
                    ratings=ratings,
                    amount=amount)

        item.set_shop_items(shop_items)
        return item

    @classmethod
    def parse_title(cls, title):
        if title[0] == "\\u2713" or title[0] == "\\u2605":
            title = title[2:]

        pos = title.find(" ")
        pos2 = title.find(" -=(")
        euro = title.find(" €", pos2)

        price = None
        num_rating = None
        if pos < 0 or not is_int(title[:pos]):
            amount = 1
            name = title
        else:
            if pos == pos2:
                amount = 1
                name = title[:pos2]
            else:
                amount = int(title[:pos])
                if pos2 > 0:
                    name = title[pos + 1:pos2]
                else:
                    name = title[pos + 1:]
            if pos2 > 0:
                price = title[pos2 + 4:euro]
                # num_rating = int(title[euro + 12:-1])

        return name, amount, price, num_rating

    @classmethod
    def parse_notes(cls, notes):
        url_pos_start = notes.find('* ')

        if url_pos_start < 0:
            return None, None, None, None

        if url_pos_start > 0:
            sub_name = notes[0: notes.find('\n\n')]
            url_pos_end = notes.find('\n\n', url_pos_start)
        else:
            sub_name = None
            url_pos_end = notes.find('\n\n')

        url = notes[url_pos_start + 2:url_pos_end]

        if notes.find("\nInhalt:\n") < 0:
            return url, None, None, sub_name

        notes = notes[url_pos_end + 2:]
        ratings_end = notes.find("\nInhalt:\n")

        end = 0
        ratings_data = []
        while 0 < end + 1 < ratings_end:
            pos = notes.find('* ', end) + 2
            end = notes.find("\n", pos)
            rating = notes[pos:end]
            ratings_data.append(rating)

        ingredients = notes[ratings_end + 9:]
        return url, ingredients, ratings_data, sub_name

    @classmethod
    def parse_subs(cls, sub_tasks):
        shop_items = []
        for item in sub_tasks:
            shop_item = ShopItem.parse(item['title'])
            shop_item.select = item['completed']
            shop_items.append(shop_item)

        return shop_items


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
