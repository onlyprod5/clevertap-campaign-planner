import os
import re
import pyotp
from time import sleep
from datetime import datetime

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def setup_browser():
    options = webdriver.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")

    driver = webdriver.Chrome(options=options)
    return driver

def quit_browser(driver):
    driver.quit()

def login(driver):
    now = datetime.now()
    totp = get_totp_instance()

    driver.get("https://eu1.dashboard.clevertap.com/65W-5R5-4R6Z/campaigns")

    sleep(1)

    element = driver.find_element(By.NAME, "username")
    element.send_keys(os.getenv('CT_EMAIL'))

    btn = driver.find_element(By.NAME, "action")
    btn.click()

    WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )

    input = driver.find_element(By.NAME, "password")
    input.send_keys(os.getenv('CT_PASSWORD'))

    btn = driver.find_element(By.NAME, "action")
    btn.click()

    otp = totp.now()

    code = driver.find_element(By.NAME, "code")
    code.send_keys(otp)

    btn = driver.find_element(By.NAME, "action")
    btn.click()

    sleep(2)

    print(f'time taken to login: {datetime.now() - now}')

    return driver.get_cookies()

def get_totp_instance():
    secret = os.getenv('OTP_SECRET')
    return pyotp.TOTP(secret)

def get_user_base(driver, campaigns):
    for campaign in campaigns:
        campaign_id = campaign.campaign_id
        now = datetime.now()

        url = f"https://eu1.dashboard.clevertap.com/65W-5R5-4R6Z/campaigns/campaign/{campaign_id}/edit"

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[2]/div/button"))
        )

        who_drawer = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[2]/div/button")
        who_drawer.click()

        sleep(1)

        edit_btn = driver.find_element(By.XPATH, "//h1[text()='Target Segment']/following-sibling::*[.//span[text()='Edit']]")
        edit_btn.click()

        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH,"/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div/div[3]/div[4]/button"))
        )

        calculate_userbase_btn = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div/div[3]/div[4]/button")
        calculate_userbase_btn.click()

        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//h1[text()='Estimated reach']/../..//span[text()='Total Reach' or text()='Total Users']/preceding-sibling::span"))
        )

        userbase_text = driver.find_element(By.XPATH, "//h1[text()='Estimated reach']/../..//span[text()='Total Reach' or text()='Total Users']/preceding-sibling::span")
        userbase = userbase_text.text

        userbase = userbase.replace(",", "")

        userbase = int(userbase)

        when_drawer = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[4]/div/button")
        when_drawer.click()

        sleep(1)

        throttle = 2**31 - 1
        try:
            element = driver.find_element(By.XPATH, "//h1[text()='Throttle limits']/..//span[contains(text(), 'per 5 mins')]")
            match = re.match(r'^(\d+)\s+messages per 5 mins$', element.text)

            if match:
                throttle = int(match.group(1))

        except NoSuchElementException:
            print(f"Throttle limit is not present for campaign {campaign.campaign_id}")

        campaign.total_audience = userbase
        campaign.throttle = throttle

        print(f'time taken by get_user_base: {datetime.now() - now}')

    return campaigns

def update_scheduled_time(driver, campaign_schedules):
    for campaign in campaign_schedules:
        print(campaign.campaign_id, campaign.original_schedule_time)
        sleep(10)
        now = datetime.now()
        driver.get(f"https://eu1.dashboard.clevertap.com/65W-5R5-4R6Z/campaigns/campaign/{campaign.campaign_id}/edit")

        sleep(2)

        when_drawer = driver.find_element(By.XPATH,"/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[4]/div/button")
        when_drawer.click()

        sleep(1)
        edit_btn = driver.find_element(By.XPATH,"/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[4]/div/div/div/div/div/div[1]/div/div[1]/div")
        edit_btn.click()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[4]/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[3]/div[1]/div/div[4]/div/label/input"))
        )

        time = driver.find_element(By.XPATH, "/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[4]/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[3]/div[1]/div/div[4]/div/label/input")
        time.clear()
        time.send_keys(f"{campaign.original_schedule_time.hour}:{campaign.original_schedule_time.minute}")

        sleep(100)
        time_submit_btn = driver.find_element(By.XPATH,"/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[4]/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div/button")
        time_submit_btn.click()

        sleep(1)
        submit_btn = driver.find_element(By.XPATH,"/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[5]/div/div/div/div/div[1]/div[2]/button")
        submit_btn.click()

        submit_btn = driver.find_element(By.XPATH,"/html/body/div[3]/div[3]/div/div/div[2]/button[1]")
        submit_btn.click()

        print(f'time taken by update_schedule_time: {datetime.now() - now}')
