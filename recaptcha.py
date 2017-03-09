import requests
from time import sleep, time

start_time = time()

# send credentials to the service to solve captcha
# returns service's captcha_id of captcha to be solved
url = "http://2captcha.com/in.php?key=1069c3052adead147d1736d7802fabe2&method=userrecaptcha&googlekey=6Lf5CQkTAAAAAKA-kgNm9mV6sgqpGmRmRMFJYMz8&pageurl=http://testing-ground.scraping.pro/recaptcha"
resp = requests.get(url)
if resp.text[0:2] != 'OK':
    quit('Error. Captcha is not received')
captcha_id = resp.text[3:]

# fetch ready 'g-recaptcha-response' token for captcha_id
fetch_url = "http://2captcha.com/res.php?key=1069c3052adead147d1736d7802fabe2&action=get&id=" + captcha_id
for i in range(1, 20):
    sleep(5)  # wait 5 sec.
    resp = requests.get(fetch_url)
    if resp.text[0:2] == 'OK':
        break

print('Time to solve: ', time() - start_time)

# final submitting of form (POST) with 'g-recaptcha-response' token
submit_url = "http://testing-ground.scraping.pro/recaptcha"
# spoof user agent
headers = {'user-agent': 'Mozilla/5.0 Chrome/52.0.2743.116 Safari/537.36'}
# POST parameters, might be more, depending on form content
payload = {'submit': 'submit', 'g-recaptcha-response': resp.text[3:]}
resp = requests.post(submit_url, headers=headers, data=payload)

