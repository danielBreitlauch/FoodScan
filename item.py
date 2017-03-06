# -*- coding: utf-8 -*-


class ShopItem:
    def __init__(self, article_id, amount, name, price, link):
        self.article_id = article_id
        self.amount = amount
        self.name = name
        self.price = price
        self.link = link

    def __unicode__(self):
        return str(self.price / 100.0) + u'€ ' + self.name + u' (' + self.link + u')'

    def __eq__(self, other):
        if isinstance(other, ShopItem):
            return self.name == other.name and self.price == other.price and self.link == other.link

        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    @classmethod
    def parse(cls, string):
        price_end = string.find(u'€ ')
        name_end = string.find(u' (', price_end)
        link_end = string.find(u')', name_end)

        price = float(string[:price_end]) * 100
        name = string[price_end + 2:name_end]
        link = string[name_end + 2:link_end]

        return ShopItem(None, None, name, price, link)


class Item:

    def __init__(self, name, cc_price=None, ingredients=None, ratings=None, cc_url=None, amount=1, num_rating=0):
        self.name = name
        self.cc_price = cc_price
        self.ingredients = ingredients
        self.ratings_data = ratings
        self.num_rating = num_rating
        self.amount = amount
        self.shop_items = None
        self.selected_item = None
        if cc_url:
            self.cc_url = cc_url
        else:
            from codecheck import CodeCheck
            self.cc_url = CodeCheck.url(self.name)

    def inc_amount(self, amount=1):
        self.amount += amount

    def add_shop_items(self, shop_items):
        if self.shop_items is None:
            self.shop_items = []

        for item in shop_items:
            item.amount = self.amount

            if item in self.shop_items:
                self.shop_items.remove(item)
            if item == self.selected_item:
                self.selected_item = item

            self.shop_items.append(item)

        if len(shop_items) == 1:
            self.selected_item = self.shop_items[0]

    def select_shop_item(self, item):
        if self.shop_items is None and item is not None:
            self.shop_items = [item]

        if item is None:
            self.selected_item = None
        else:
            for i in self.shop_items:
                if i == item:
                    self.selected_item = i

            self.selected_item.amount = self.amount

    def selected_shop_item(self):
        self.selected_item.amount = self.amount
        return self.selected_item

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name

        return NotImplemented

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
        price = self.cc_price
        if self.synced():
            title = u"\u2713 "
            price = self.selected_item.price
        elif self.searched():
            title = u"\u2605 "

        title += str(self.amount) + " " + self.name

        if price and price > 0:
            title += " -=(" + str(price / 100.0) + u'€)'

        return title

    def note(self):
        note = '* ' + self.cc_url + '\n\n'

        if self.ratings_data:
            for rating in self.ratings_data:
                note += '* ' + rating + '\n'

        if self.ingredients:
            note += '\nInhalt:\n' + self.ingredients

        return note

    @classmethod
    def parse(cls, title, notes, completed_subs):
        name, amount, price, num_rating = cls.parse_title(title)
        cc_url, ingredients, ratings = cls.parse_notes(notes)
        shop_item = cls.parse_completed_subs(completed_subs)

        item = Item(name=name,
                    ingredients=ingredients,
                    cc_url=cc_url,
                    ratings=ratings,
                    amount=amount,
                    num_rating=num_rating)

        if shop_item:
            item.select_shop_item(shop_item)

        return item

    @classmethod
    def parse_title(cls, title):
        shop_state = None
        if title[0] == u"\u2713":
            shop_state = "synced"
        elif title[0] == u"\u2605":
            shop_state = "searched"

        if title[0] == u"\u2713" or title[0] == u"\u2605":
            title = title[2:]

        pos = title.find(" ")
        pos2 = title.find(" -=(")
        euro = title.find(u" €", pos2)

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
        url_pos = notes.find('\n\n')
        if url_pos <= 0:
            return None, None, None

        url = notes[2:url_pos]

        if notes.find("\nInhalt:\n") < 0:
            return url, None, None

        notes = notes[url_pos:]
        ratings_end = notes.find("\nInhalt:\n")

        end = 0
        ratings_data = []
        while 0 < end + 1 < ratings_end:
            pos = notes.find('* ', end) + 2
            end = notes.find("\n", pos)
            rating = notes[pos:end]
            ratings_data.append(rating)

        ingredients = notes[ratings_end + 9:]
        return url, ingredients, ratings_data

    @classmethod
    def parse_completed_subs(cls, completed_subs):
        if len(completed_subs) == 0:
            return None

        shop_items = []
        for item in completed_subs:
            shop_items.append(ShopItem.parse(item['title']))

        return shop_items[0]


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
