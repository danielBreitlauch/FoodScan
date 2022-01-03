import io
import json
from random import randrange

from requests import *
import gzip
from FoodScan.ShopList import ShopList, Item
from FoodScan.items import is_int, ShopItem


class Paprika3List(ShopList):

    paprikaRestURL = "https://www.paprikaapp.com/api/v2/"
    paprikaBearerToken = ""
    paprikaListUUID = ""

    def __init__(self, config):
        ShopList.__init__(self)
        self.paprikaListUUID = config['listID']
        self.login(config['email'], config['password'])

    def is_meta_item(self, task):
        return False

    def create_web_hook(self, url, port):
        pass

    def list_tasks(self):
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer %s" % self.paprikaBearerToken
        }

        items = get(self.paprikaRestURL + "sync/groceries/", headers=headers).json()
        return [x for x in items['result'] if x['list_uid'] == self.paprikaListUUID]

    def item_from_task(self, task, with_selects=True):
        if 'quantity' in task and task['quantity'] is not None and is_int(task['quantity']):
            amount = int(task['quantity'])
        else:
            amount = 1

        name = task['name']
        position = name.find(' ')
        if position > 0:
            possible_amount = name[0:position]
            if is_int(possible_amount):
                name = name[position + 1:]
                amount = int(possible_amount)

        if task['purchased']:
            amount = 0

        item = Item(name=name, amount=amount)
        item.select_shop_item(ShopItem(task['uid'], amount, name, None, None, True))
        return item

    def create_item(self, item):
        shop_item = item.selected_shop_item()
        item_str = [
            {
                "uid": str(randrange(1000000)),
                "order_flag": 0,
                "purchased": False,
                "quantity": str(item.amount),
                "list_uid": self.paprikaListUUID,
                "name": str(item.amount) + " " + item.name
            }
        ]
        if shop_item and shop_item.article_id:
            item_str[0]["uid"] = shop_item.article_id

        files = {'data': self.gzip(json.dumps(item_str))}
        post(self.paprikaRestURL + "sync/groceries", files=files, headers={
            'Authorization': "Bearer %s" % self.paprikaBearerToken,
        })

    def update_item(self, task, item, rebuild_notes=False, rebuild_subs=False):
        self.create_item(item)

    def delete_item(self, task):
        raise NotImplementedError('users must define __str__ to use this base class')

    def list_revision(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    def task_sub_tasks(self, iid):
        raise NotImplementedError('users must define __str__ to use this base class')

    def task_position(self, iid, position):
        raise NotImplementedError('users must define __str__ to use this base class')

    def gzip(self, content):
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode='w') as fo:
            fo.write(content.encode())
        bytes_obj = out.getvalue()
        return bytes_obj

    def encode_multipart_formdata(self, fields):
        boundary = "---011000010111000001101001"
        body = (
            "".join("--%s\r\n"
                    "Content-Disposition: form-data; name=\"%s\"\r\n"
                    "\r\n"
                    "%s\r\n" % (boundary, field, value)
                    for field, value in fields.items()) +
            "--%s--\r\n" % boundary
        )

        content_type = "multipart/form-data; boundary=%s" % boundary
        return body, content_type

    def login(self, email, password):
        body, content_type = self.encode_multipart_formdata({
            'email': email,
            'password': password
        })

        response = post(self.paprikaRestURL + "account/login/", data=body, headers={
            'Content-Type': content_type
        })

        if response.status_code == 200:
            json = response.json()
            if json != "":
                self.paprikaBearerToken = json['result']['token']
                return

        print("Wrong credentials")
        exit(1)

    def search(self, name):
        raise NotImplementedError('users must define __str__ to use this base class')

    def lists(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    def user_settings(self):
        raise NotImplementedError('users must define __str__ to use this base class')

