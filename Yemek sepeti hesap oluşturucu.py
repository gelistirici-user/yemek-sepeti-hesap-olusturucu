from bs4 import BeautifulSoup as bs
import requests
import random
import string
import time
import json

def get_user_data(mail_length):
    mail = ''.join(random.choice(string.ascii_letters+string.digits) for i in range(mail_length))
    name_data = json.loads(requests.get('http://rp.burakgarci.net/api.php', headers={'user-agent': 'Mozilla/5.0'}).text)
    birth = f'0{random.choice(range(9))}.0{random.choice(range(9))}.{random.choice(range(1979, 2003))}'
    return mail, name_data['isim'], name_data['soyisim'], birth

def config():
    return json.loads(open('config.json', 'r', encoding='UTF-8').read())

def proxies(path):
    proxies = []
    with open(path, 'r', encoding='UTF-8') as f:
        for proxy in f.readlines():
            if proxy != '':
                proxies.append(proxy.strip())
    return proxies

def register(mail, pwd, name, lastname, birth, proxy, country):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "tr-TR,tr;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.yemeksepeti.com",
        "referer": f"https://www.yemeksepeti.com/{country}-uye-ol",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    }

    with requests.session() as session:
        session.headers.update({'user-agent': 'Mozilla/5.0'})
        session.proxies.update({'http': 'https://' + proxy})

        r = session.get(f'https://www.yemeksepeti.com/{country}-uye-ol')
        soup = bs(r.content, 'html5lib')

        area_id = soup.find('select', {'name': 'AreaId'}).find_all('option')[1]['value']
        verification_token = soup.find('input', {'name': '__RequestVerificationToken'})['value']

        session.headers.update(headers)

        payload = {
            "__RequestVerificationToken": verification_token,
            "Email": mail,
            "Password": pwd,
            "RepeatPassword": pwd,
            "FirstName": name,
            "LastName": lastname,
            "BirthDate": birth,
            "AreaId": area_id,
            "AcceptEula": "true",
            "inputAcceptEula": "false",
            "inputEmailNotification": "false",
            "inputSmsNotification": "false",
            "Referrer": "/hosgeldiniz?source=register"
        }

        r = session.post(f'https://www.yemeksepeti.com/{country}-uye-ol', data=payload)
        if r.cookies['gameToken']:
            return True

config = config()
proxies = proxies(config['proxy_file_path'])
banned_proxies = []

for tour in range(config['account_per_proxy']):
    for proxy in proxies:
        if proxy not in banned_proxies:
            mail, name, lastname, birth = get_user_data(config['mail_length'])
            mail = mail + config['mail_domain']

            try:
                if register(mail, config['password'], name, lastname, birth, proxy, config['country']):
                    with open(config['results_file_path'], 'a', encoding='UTF-8') as f:
                        f.write(f"{mail}:{config['password']}\n")
                    print(f"[ + ] Hesap oluşturuldu! {mail}:{config['password']}")

                else:
                    print(f"[ - ] Hesap oluşturulamadı pas geçiliyor...")
            except Exception as e:
                if proxy not in banned_proxies:
                    print(f"\nHesap oluşturulamadı proxy banlı: {proxy}\n")
                    banned_proxies.append(proxy)


input("\n\n\nÇıkmak için enter tuşuna basınız >> ")
