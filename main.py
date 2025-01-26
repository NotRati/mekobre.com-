import requests
import random
import string
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
class SeleniumBot:
    def __init__(self):
        self.options = Options()
        # self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)

    def login(self, mail, password):
        self.driver.get('https://mekobre.com/login')
        self.driver.find_element(By.NAME, 'email').send_keys(mail)
        self.driver.find_element(By.NAME, 'password').send_keys(password)
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    def get_checksum(self, url):
        self.driver.get(url)
        comment_element = self.driver.find_element(By.ID, 'comment')
        self.driver.implicitly_wait(1)
        ActionChains(self.driver).move_to_element(comment_element).perform()
        comment_element.send_keys("1212341c34c1341c234")
        comment_element.submit()
        time.sleep(1)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find the div with the wire:snapshot attribute
        div = soup.find('div', {'wire:snapshot': True})
        if div:
            wire_snapshot = div['wire:snapshot']
            snapshot_data = json.loads(wire_snapshot)
            checksum = snapshot_data.get('checksum')
            print("Checksum:", checksum)
            return checksum
        else:
            print("Checksum not found")
            return None

class Bot:
    def __init__(self):
        self.session = requests.Session()
        self.domain = "mekobre.com"
        self.headers = {}
        self.get_csrf_token()
        self.wire_snapshot = [[], []]
        print("CSRF Token:", self.csrf_token)
        print("COOKIES:", self.cookies.keys())
    def sign_up(self):
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        mail = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) + '@gmail.com'
        nickname = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        data = {
            '_token': self.csrf_token,
            'name': nickname,
            'username': nickname,
            'email': mail,
            'password': password,
        }
        self.mail = mail
        self.password = password
        response = requests.post(f'https://mekobre.com/register', headers=self.headers, data=data, cookies=self.cookies)
        print(mail, password)
        print(response.status_code)
        self.cookies = response.cookies
    def post_comment(self):
        json_data = {
            '_token': self.csrf_token,
            'components': [
            {
                'snapshot': self.wire_snapshot[0],
                'updates': {
                'newCommentState.body': 'au ra magari filmi',
                },
                'calls': [
                {
                    'path': '',
                    'method': 'postComment',
                    'params': [],
                },
                ],
            },
            ],
        }
        for i in range(100):
            response = self.session.post('https://mekobre.com/livewire/update', cookies=self.cookies, headers=self.headers, json=json_data)
            print(response.status_code)
    def set_headers(self):
        pass
    def get_csrf_token(self):
        response = requests.get(f'https://{self.domain}')
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_meta = soup.find('meta', attrs={'name': 'csrf-token'})
        if csrf_meta:
            self.csrf_token = csrf_meta.get('content')
        else:
            print("CSRF Token not found")
            exit()
        self.cookies = response.cookies
    def get_login_details(self):
        return (self.mail, self.password)
    def extract_checksum(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        div = soup.find('div', {'wire:snapshot': True})
        if div:
            wire_snapshot = div['wire:snapshot']
            snapshot_data = json.loads(wire_snapshot)
            checksum = snapshot_data.get('checksum')
            print("Checksum:", checksum)
            return checksum
        else:
            print("Checksum not found")
            return None
    def get_checksum(self, url):
        response = self.session.get(url)
        self.checksum_comment = self.extract_checksum(response.text)
        return self.checksum_comment
    def extract_snapshot(self, url):
        self.url = url
        response = self.session.get(url)
        #COMMENT SNAPSHOT
        soup = BeautifulSoup(response.text, 'html.parser')
        div_snapshot = soup.find('div', {'class': 'pb-6'})
        if div_snapshot:
            div = div_snapshot.find('div', {'wire:snapshot': True})
            if div:
                wire_snapshot = div['wire:snapshot']
                wire_snapshot = wire_snapshot.replace('&quot', '"')                
                # print(wire_snapshot)
                self.wire_snapshot[0] = wire_snapshot
                
            else:
                print("Snapshot not found")
                return None
        #LIKE SNAPSHOT
        div_snapshot = soup.find('div', {'class': 'flex items-center gap-x-1'}) #only works for moana 2 TODO : make it work for all movies
        if div_snapshot:
            wire_snapshot = div_snapshot['wire:snapshot']
            wire_snapshot = wire_snapshot.replace('&quot', '"')
            # print(wire_snapshot)
            self.wire_snapshot[1] = wire_snapshot
        else:
            print("Snapshot not found")
            return None
    def like_movie(self):
        json_data = {
            '_token': self.csrf_token,
            'components': [
            {
                'snapshot': self.wire_snapshot[1],
                'updates': {
                },
                'calls': [
                {
                    'path': '',
                    'method': 'reactionButton',
                    'params': [
                        'like',
                    ],
                },
            ],
            },
            ],
        }
        response = self.session.post('https://mekobre.com/livewire/update', cookies=self.cookies, headers=self.headers, json=json_data)
        print(response.status_code)
    def logout(self):
        response = requests.get('https://mekobre.com/logout', cookies=self.cookies, headers=self.headers)
while True:
    bot = Bot()
    bot.sign_up()
    bot.extract_snapshot('https://mekobre.com/movie/moana-2')
    bot.like_movie()
    bot.logout()