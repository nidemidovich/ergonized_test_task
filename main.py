import logging
import random
import os
import secrets
import string
import time

import requests


logging.basicConfig(
    level=logging.INFO,
    format=f"\u001b[36;1m[\u001b[0m%(asctime)s\u001b[36;1m]\u001b[0m -> \u001b[36;1m%(message)s\u001b[0m",
    datefmt="%H:%M:%S",
)

def registration(token, proxy=None) -> str:
    site = 'https://discord.com/register'
    sitekey = '4c672d35-0701-42b2-88c3-78380b0db560'

    proxy_for_api = None
    if proxy:
        proxy_for_api = list(proxy.values())[0].split('//')[-1]

    logging.info('Generating the credentials...')
    username, email, password = genereate_credentials(random.randint(5, 10))
    logging.info('The credentials has been generated.')
    
    logging.info('Solving the captcha...')
    captcha_key = solve_captcha(site, sitekey, token, proxy=proxy_for_api)
    logging.info('The captcha has been solved.')

    data = {
        "fingerprint": "939057976310915102.H-LxsGoBXYUk3A-OrAFVjOi5x4k",
        "email": email,
        "username": username,
        "password": password,
        "invite": None,
        "consent": True,
        "date_of_birth": "1994-05-05",
        "gift_code_sku_id": None,
        "captcha_key": captcha_key
    }

    headers = {
        "Host": "discord.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "X-Super-Properties": "eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS85Mi4wLjQ1MTUuMTMxIFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiI5Mi4wLjQ1MTUuMTMxIiwib3NfdmVyc2lvbiI6IjEwLjE1LjciLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6OTI3OTIsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9",
        "X-Fingerprint": "",
        "Accept-Language": "en-US",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "Content-Type": "application/json",
        "Authorization": "undefined",
        "Accept": "*/*",
        "Origin": "https://discord.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://discord.com/register",
        "X-Debug-Options": "bugReporterEnabled",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": "OptanonConsent=version=6.17.0; locale=th"
    }
    url = 'https://discord.com/api/v9/auth/register'
    logging.info('Sending POST request to discord auth service...')
    response = requests.post(url, json=data, proxies=proxy, headers=headers)
    
    try:
        token = response.json()['token']
        logging.info('Successful registration!')
        logging.info(f'Current token is {token}')
        with open('generated.txt', 'a+') as writer:
            writer.write(f'{email}:{password}:{token}'+'\n')
    except:
        logging.info(f'Something went wrong! Here is the response: {response.json()}')
        logging.info('Try to use another proxy.')



def genereate_credentials(char_num) -> tuple:
    username =  ''.join(random.choice(string.ascii_letters) for _ in range(char_num))
    email = username + '@gmail.com'

    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))

    return username, email, password


def solve_captcha(site, sitekey, token, proxy=None) -> str:
    key = 'key=' + token
    sitekey = '&sitekey=' + sitekey
    need_json = '&json=1'
    proxy_param = ''
    if proxy:
        proxy_param = '$proxy=' + proxy
    
    in_endpoint = 'https://2captcha.com/in.php?'
    method = '&method=hcaptcha'
    site = '&pageurl=' + site
    post_req = in_endpoint + key + method + sitekey + need_json + proxy_param + site
    
    response = requests.post(post_req)
    if response.json()['status'] == 1:
        captcha_id = response.json()['request']
    else:
        return False
    
    time.sleep(15)

    res_endpoint = 'https://2captcha.com/res.php?'
    action = '&action=get'
    id = '&id=' + captcha_id
    get_req = res_endpoint + key + action + need_json + proxy_param + id

    response = requests.get(get_req)
    while response.json()['request'] == 'CAPCHA_NOT_READY':
        time.sleep(5)
        response = requests.get(get_req)
    
    return response.json()['request'].rstrip()


if __name__ == '__main__':
    token = os.getenv('API_TOKEN')
    registration(token)
