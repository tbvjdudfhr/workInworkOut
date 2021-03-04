import datetime
import os
import platform
from tkinter import *

import chromedriver_autoinstaller
import yaml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import subprocess
import time

_CONFIG_PATH = './config/info.yml'
_PLATFORM = platform.system()


class WorkTime:
    start_work_time_str = None
    end_work_time_str = None


# directory 경로에 폴더 생성
def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


# 경로 반환
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# conf 파일 로드
with open(resource_path(_CONFIG_PATH)) as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)


# 드라이버 반환
def init_driver():
    # 크롬드라이버 설치
    chrome_path = chromedriver_autoinstaller.install(cwd=True)

    # 백그라운드 실행 옵션 추가
    options = webdriver.ChromeOptions()

    if not (conf['isDebug']):
        options.add_argument("headless")

    driver = webdriver.Chrome(chrome_path, options=options)
    driver.implicitly_wait(30)
    driver.get(conf['url'])

    return driver


# 페이지 로드 대기
def wait_load(elm_id, driver):
    try:
        element = WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.ID, elm_id))
        )
    except TimeoutException:
        print("Failed to find element " + elm_id)
        driver.quit()


def find_time_group(driver):
    elm_time_group = driver.find_element_by_xpath(
        "//*[@id='summary']/div/div[1]/div[1]/span[1]/span[2]")

    work_time = WorkTime()
    work_time.start_work_time_str = elm_time_group.text.split('~')[0].strip()
    work_time.end_work_time_str = elm_time_group.text.split('~')[1].strip()

    return work_time


def main():
    # 로그 폴더 생성
    create_folder(resource_path('logs'))

    # 브라우저 실행
    driver = init_driver()

    # 로그인 진행
    elm_username = driver.find_element_by_id('username')
    elm_password = driver.find_element_by_id('password')
    elm_login_submit = driver.find_element_by_id('login_submit')

    elm_username.send_keys(conf['id'])
    elm_password.send_keys(conf['pwd'])

    elm_login_submit.click()

    # 페이지 로드 대기
    wait_load('overtime', driver)
    time.sleep(5)

    # 설정된 출근 시간 확인
    work_time = find_time_group(driver)

    # 현재 날짜, 구분(오전/오후)설정
    now_date_time = datetime.datetime.today()
    now_date_time_str = now_date_time.strftime('%Y-%m-%d')
    time_division = datetime.datetime.now().strftime('%p')

    # 출, 퇴근 시간 설정
    start_work_time_str = now_date_time_str + ' ' + work_time.start_work_time_str
    end_work_time_str = now_date_time_str + ' ' + work_time.end_work_time_str

    start_work_time = datetime.datetime.strptime(start_work_time_str, '%Y-%m-%d %H:%M:%S')
    end_work_time = datetime.datetime.strptime(end_work_time_str, '%Y-%m-%d %H:%M:%S')

    is_success = False
    # result_msg = 'No message'

    if time_division == 'AM':
        # 오전인 경우 출근 처리
        elm_work_in = driver.find_element_by_id('workIn')

        if not (conf['isDebug']):
            elm_work_in.click()

        is_success = True
        # result_msg = "출근 처리 시간 : {}".format(now_date_time.strftime('%Y-%m-%d %H:%M:%S'))

    else:
        # 오후인 경우 퇴근 처리(오동작방지를 위해 퇴근시간 이후부터 작동)
        if now_date_time > end_work_time:
            elm_work_out = driver.find_element_by_id('workOut')

            if not (conf['isDebug']):
                elm_work_out.click()

            is_success = True
            # result_msg = "퇴근 처리 시간 : {}".format(now_date_time.strftime('%Y-%m-%d %H:%M:%S'))

        else:
            # result_msg = "퇴근시간 이후({}) 처리 가능 \n현재 시간 : {}".format(end_work_time_str,
            #                                                      now_date_time.strftime('%Y-%m-%d %H:%M:%S'))
            is_success = False

    # 스크린샷 생성 후 실
    log_img_path = resource_path(
        'logs/' + time_division + '_' + now_date_time.strftime(
            '%Y%m%d_%H_%M_%S') + ('_success' if is_success else '_failed') + '.png')

    driver.get_screenshot_as_file(log_img_path)
    subprocess.call(['open', log_img_path])

    # 드라이버 종료
    driver.quit()


if __name__ == "__main__":
    main()
