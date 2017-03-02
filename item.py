# -*- coding: utf-8 -*-


class ShopItem:

    def __init__(self, article_id, amount, name, price, link):
        self.article_id = article_id
        self.amount = amount
        self.name = name
        self.price = price
        self.link = link


class Item:

    def __init__(self, name, cc_price=None, ingredients=None, ratings=None, amount=1, num_rating=0, ayn_state=None, cc_url=None):
        self.name = name
        self.cc_price = cc_price
        self.ingredients = ingredients
        self.ratings_data = ratings
        self.num_rating = num_rating
        self.amount = amount
        self.ayn_state = ayn_state
        self.ayn_items = []
        if cc_url:
            self.cc_url = cc_url
        else:
            from codecheck import CodeCheck
            self.cc_url = CodeCheck.url(self.name)

    def inc_amount(self, amount=1):
        self.amount += amount

    def add_shop_items(self, ayn_items):
        if self.ayn_state is None:
            self.set_searched()
        for item in ayn_items:
            item.amount = self.amount
            self.ayn_items.append(item)

    def synced_shop_item(self):
        item = self.ayn_items[0]
        item.amount = self.amount
        return item

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name and self.ayn_state == other.ayn_state

        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def synced(self):
        return self.ayn_state == "synced"

    def set_synced(self):
        self.ayn_state = "synced"

    def searched(self):
        return self.ayn_state == "searched"

    def set_searched(self):
        self.ayn_state = "searched"

    def title(self):
        title = ""
        price = self.cc_price
        if self.synced():
            title = u"\u2713 "
            price = self.ayn_items[0].price
        if self.searched():
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
    def parse(cls, title, notes):
        ayn_state, name, amount, price, num_rating = cls.parse_title(title)
        cc_url, ingredients, ratings = cls.parse_notes(notes)

        return Item(name=name,
                    ingredients=ingredients,
                    cc_url=cc_url,
                    ratings=ratings,
                    amount=amount,
                    num_rating=num_rating,
                    ayn_state=ayn_state)

    @classmethod
    def parse_title(cls, title):
        ayn_state = None
        if title[0] == u"\u2713":
            ayn_state = "synced"
        elif title[0] == u"\u2605":
            ayn_state = "searched"

        if ayn_state:
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

        return ayn_state, name, amount, price, num_rating

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


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
