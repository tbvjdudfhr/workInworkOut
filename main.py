from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import chromedriver_autoinstaller
import time
import yaml
import sys
import os

# chromedriver 자동 설치
chrome_path = chromedriver_autoinstaller.install(cwd=True)
browser = webdriver.Chrome(chrome_path)

browser.get('http://smart.kstec.co.kr')
time.sleep(2)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


file_path = resource_path('./config/info.yml')

# yml 정보 가져오기
with open(file_path) as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)

loginId = browser.find_element_by_id('username')
loginId.send_keys(conf['id'])

loginPwd = browser.find_element_by_id('password')
loginPwd.send_keys(conf['pwd'])
loginPwd.send_keys(Keys.RETURN)
time.sleep(2)

now = datetime.now()
ampm = now.strftime('%p')

# 현재시간이 오전이면 출근 오후면 퇴근 클릭
workBtn = browser.find_element_by_id('workIn') if ampm == 'AM' else browser.find_element_by_id('workOut')
workBtn.click()

time.sleep(2)

browser.quit()
