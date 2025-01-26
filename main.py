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
from colorama import Fore, init
import logging
import colorlog
import pyfiglet
import shutil
init(autoreset=True)

logging.addLevelName(25, 'SUCCESS')
def success(self, message, *args, **kws):
    if self.isEnabledFor(25):
        self._log(25, message, args, **kws)
logging.Logger.success = success

class SeleniumBot:
    def __init__(self):
        self.options = Options()
        # self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.logger = logging.getLogger('SeleniumBot')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(asctime)s %(message)s [Line: %(lineno)d]",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'magenta',
                'SUCCESS': 'green',
            }
        )
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def login(self, mail, password):
        self.logger.info("Logging in with email: %s", mail)
        self.driver.get('https://mekobre.com/login')
        self.driver.find_element(By.NAME, 'email').send_keys(mail)
        self.driver.find_element(By.NAME, 'password').send_keys(password)
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        self.logger.success("Logged in successfully")

    def get_checksum(self, url):
        self.logger.info("Getting checksum for URL: %s", url)
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
            self.logger.success("Checksum: %s", checksum)
            return checksum
        else:
            self.logger.error("Checksum not found")
            return None

class Bot:
    def __init__(self):
        self.session = requests.Session()
        self.domain = "mekobre.com"
        self.headers = {}
        self.wire_snapshot = [[], []]
        self.logger = logging.getLogger('Bot')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)
        # Create a colored formatter
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(asctime)s %(message)s [Line: %(lineno)d]",
            datefmt="%Y-%m-%d %H:%M:%S",  # Format for the time
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'magenta',
                'SUCCESS': 'green',
            }
        )
        ch.setFormatter(formatter)
        terminal_width = shutil.get_terminal_size().columns
        ascii_banner = pyfiglet.figlet_format("Mekobre.com   Bot \n made by rat", font="slant", width=terminal_width)
        print(Fore.BLUE + ascii_banner)
        self.get_csrf_token()

    def sign_up(self):
        self.logger.info("Signing up a new user")
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
        self.cookies = response.cookies
        if response.ok:
            self.logger.success("Sign up successful")
        else:
            self.logger.error("Sign up failed with status code: %s", response.status_code)

    def post_comment(self, comment):
        self.logger.info("Posting comment: %s", comment)
        json_data = {
            '_token': self.csrf_token,
            'components': [
            {
                'snapshot': self.wire_snapshot[0],
                'updates': {
                'newCommentState.body': f'{comment}',
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
        
        response = self.session.post('https://mekobre.com/livewire/update', cookies=self.cookies, headers=self.headers, json=json_data)
        if response.ok:
            self.logger.success("Comment posted successfully")
        else:
            self.logger.error("Failed to post comment with status code: %s", response.status_code)

    def set_headers(self):
        self.logger.info("Setting headers")
        # ...existing code...

    def get_csrf_token(self):
        self.logger.info("Getting CSRF token")
        response = requests.get(f'https://{self.domain}')
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_meta = soup.find('meta', attrs={'name': 'csrf-token'})
        if csrf_meta:
            self.csrf_token = csrf_meta.get('content')
            self.logger.success("CSRF Token obtained")
        else:
            self.logger.error("CSRF Token not found")
            exit()
        self.cookies = response.cookies

    def get_login_details(self):
        self.logger.info("Getting login details")
        return (self.mail, self.password)

    def extract_checksum(self, html_content):
        self.logger.info("Extracting checksum from HTML content")
        soup = BeautifulSoup(html_content, 'html.parser')
        div = soup.find('div', {'wire:snapshot': True})
        if div:
            wire_snapshot = div['wire:snapshot']
            snapshot_data = json.loads(wire_snapshot)
            checksum = snapshot_data.get('checksum')
            self.logger.success("Checksum: %s", checksum)
            return checksum
        else:
            self.logger.error("Checksum not found")
            return None

    def get_checksum(self, url):
        self.logger.info("Getting checksum for URL: %s", url)
        response = self.session.get(url)
        self.checksum_comment = self.extract_checksum(response.text)
        return self.checksum_comment

    def extract_snapshot(self, url):
        self.logger.info("Extracting snapshot from URL: %s", url)
        self.url = url
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        div_snapshost = soup.find_all('div', {'wire:snapshot': True})
        for div_snapshot in div_snapshost:
            wire_snapshot = div_snapshot['wire:snapshot']
            wire_snapshot = wire_snapshot.replace('&quot', '"')
            snapshot_data = json.loads(wire_snapshot)
            snapshot_name = snapshot_data["memo"]["name"]
            if snapshot_name == "comments":
                self.wire_snapshot[0] = wire_snapshot
            elif snapshot_name == "reaction-component":
                self.wire_snapshot[1] = wire_snapshot
        self.logger.success("Snapshot extracted successfully")

    def like_movie(self):
        self.logger.info("Liking movie")
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
        if response.ok:
            self.logger.success("Movie liked successfully")
        else:
            self.logger.error("Failed to like movie with status code: %s", response.status_code)

    def logout(self):
        self.logger.info("Logging out")
        response = requests.get('https://mekobre.com/logout', cookies=self.cookies, headers=self.headers)
        if response.ok:
            self.logger.success("Logged out successfully")
        else:
            self.logger.error("Failed to log out with status code: %s", response.status_code)

bot = Bot()
bot.sign_up()
bot.extract_snapshot('https://mekobre.com/movie/kazino-ischiashi')
bot.logger.info("Snapshot: %s", bot.wire_snapshot)
bot.like_movie()
bot.post_comment('wocdascasdw')
bot.logout()