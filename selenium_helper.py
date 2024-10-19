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
        try:
            campaign_id = campaign.campaign_id
            now = datetime.now()

            url = f"https://eu1.dashboard.clevertap.com/65W-5R5-4R6Z/campaigns/campaign/{campaign_id}/edit"

            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[2]/div/button"))
            )

            sleep(2)

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

            sleep(1)
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
        except Exception as e:
            print(f"Exception occurred while getting userbase of campaign : {campaign.campaign_id}")
            raise e

        print(f'time taken by get_user_base: {datetime.now() - now}')

    return campaigns

def update_scheduled_time(driver, campaign_schedules):
    campaign_update_status = {}

    for campaign in campaign_schedules:
        try:
            if campaign.preferred_schedule_time is None or campaign.preferred_schedule_time == campaign.original_schedule_time:
                continue

            driver.get(f"https://eu1.dashboard.clevertap.com/65W-5R5-4R6Z/campaigns/campaign/{campaign.campaign_id}/edit")

            sleep(2)

            when_drawer = driver.find_element(By.XPATH,"/html/body/div[3]/div/main/div/section/div/div/div[2]/div/div[4]/div/button")
            when_drawer.click()

            sleep(1)
            edit_btn = driver.find_element(By.XPATH,"//h1[text()='Date and time']/following-sibling::*[.//span[text()='Edit']]")
            edit_btn.click()

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[text()='A fixed time']/../../../../../../.././following-sibling::*//input"))
            )

            time = driver.find_element(By.XPATH, "//div[text()='A fixed time']/../../../../../../.././following-sibling::*//input")
            time.clear()
            time.send_keys(f"{campaign.preferred_schedule_time.hour}:{campaign.preferred_schedule_time.minute}")

            sleep(100)
            time_submit_btn = driver.find_element(By.XPATH,"//span[text()='Done']")
            time_submit_btn.click()

            sleep(1)
            submit_btn = driver.find_element(By.XPATH,"//span[text()='All Done!']//following-sibling::*/following-sibling::*")
            submit_btn.click()

            submit_btn = driver.find_element(By.XPATH,"/html/body/div[3]/div[3]/div/div/div[2]/button[1]")
            submit_btn.click()

            sleep(3)

            if True:
                campaign_update_status[campaign.campaign_id] = 'UPDATED'
            else:
                campaign_update_status[campaign.campaign_id] = 'NOT_UPDATED'
        except Exception as e:
            print(f'ERROR - {e}')
            campaign_update_status[campaign.campaign_id] = str(e)


    return campaign_update_status