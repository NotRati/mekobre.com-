import requests
import random
import string
from bs4 import BeautifulSoup
import json

class Bot:
    def __init__(self):
        self.session = requests.Session()
        self.domain = "mekobre.com"
        self.headers = {}
        self.get_csrf_token()
        self.wire_snapshot = []
        self.snapshot_extracted = False
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

    def extract_snapshot(self, url):
        if not self.snapshot_extracted:
            print("Extracting snapshot...")
            self.url = url
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # COMMENT SNAPSHOT
            div_snapshot = soup.find('div', {'class': 'pb-6'})
            if div_snapshot:
                div = div_snapshot.find('div', {'wire:snapshot': True})
                if div:
                    wire_snapshot = div['wire:snapshot']
                    wire_snapshot = wire_snapshot.replace('&quot', '"')                
                    print(wire_snapshot)
                    self.wire_snapshot.append(wire_snapshot)  # Store the snapshot
                else:
                    print("Snapshot not found")
                    return None
            
            # LIKE SNAPSHOT
            div_snapshot = soup.find('div', {'class': 'notify fixed bottom-0 right-0 flex items-center w-full max-w-sm justify-center px-6 py-8 pointer-events-none z-50'})
            if div_snapshot:
                wire_snapshot = div_snapshot['wire:snapshot']
                wire_snapshot = wire_snapshot.replace('&quot', '"')
                print(wire_snapshot)
                self.wire_snapshot.append(wire_snapshot)

            self.snapshot_extracted = True
        else:
            print("Snapshot already extracted, skipping...")

    def like_movie(self):
        if not self.snapshot_extracted:
            print("Snapshot not extracted yet, please extract it first!")
            return

        json_data = {
            '_token': self.csrf_token,
            'components': [
            {
                'snapshot': self.wire_snapshot[1],
                "updates":{},"calls":[{"path":"","method":"reactionButton","params":["like"]}]
            },
            ],
        }
        response = self.session.post('https://mekobre.com/livewire/update', cookies=self.cookies, headers=self.headers, json=json_data)
        print(response.status_code)

    def post_comment(self):
        if not self.snapshot_extracted:
            print("Snapshot not extracted yet, please extract it first!")
            return

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

while True:
    bot = Bot()
    bot.sign_up()
    bot.extract_snapshot('https://mekobre.com/movie/moana-2') 
    bot.like_movie()  

