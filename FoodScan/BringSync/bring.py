from requests import *


class Bring:

    url = 'https://api.getbring.com/rest/v2/bringtemplates'

    generic_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'br',
        'Accept-Language': 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4'
    }

    def __init__(self, config):
        self.auth_headers = {
            'X-BRING-API-KEY': config['api_key'],
            'X-BRING-USER-UUID': config['user_uuid'],
            'X-BRING-CLIENT': 'webApp',
            'Authorization': config['authentication'],
            'Cookie': config['cookie']
        }

    def upload(self, items, name="Einkauf"):
        headers = self.generic_headers.copy()
        headers.update(self.auth_headers)

        item_arr = []
        for item in items:
            item_arr.append({"itemId": item.name, "spec": item.amount})
        data = {
            "userUuid": "cff0acda-fe65-4b50-9766-d55ac749ea83",
            "type": "RECIPE",
            "content": {
                "name": name,
                "imageUrl": "https://www.vitalingo.com/media/image/obst-gemuese-nahrungsergaenzung.jpg",
                "items": item_arr
            }
        }

        post(self.url, data=data, headers=headers)

