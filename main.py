import os
import time
from datetime import datetime
from tkinter import *

import chromedriver_autoinstaller
import yaml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# chromedriver 자동 설치
chrome_path = chromedriver_autoinstaller.install(cwd=True)
options = webdriver.ChromeOptions()
options.add_argument("headless")

browser = webdriver.Chrome(chrome_path, options=options)

browser.get('http://smart.kstec.co.kr')
time.sleep(2)


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


file_path = resource_path('./config/info.yml')

createFolder(resource_path('logs'))

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

# 결과 메시지 박스 출력
imgPath = resource_path('logs\\' + ampm + now.strftime('%Y%m%d_%H_%M_%S') + '.png')
print(imgPath)
browser.get_screenshot_as_file(imgPath)
time.sleep(2)

msgBox = Tk()
resultImg = PhotoImage(file=imgPath)
imgLabel = Label(image=resultImg)
imgLabel.image = resultImg
imgLabel.pack()
imgLabel.place(x=0, y=0)

title = '출근처리 결과' if ampm == 'AM' else '퇴근처리 결과'

msgBox.title(title)
msgBox.geometry('700x500+10+10')
msgBox.mainloop()

time.sleep(2)

browser.quit()
