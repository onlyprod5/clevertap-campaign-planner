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
import constants
from link_validator import LinkValidatorFactory, validate_link_domain
from validator import validate_metadata_for_ios_and_android

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

    driver.get(f"https://eu1.dashboard.clevertap.com/{os.getenv('CT_ACC_ID')}/campaigns")

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

def get_campaign_metadata(driver, campaigns):
    for campaign in campaigns:
        try_count = 2
        captured_exception = None

        if campaign.channel != 'push':
            continue

        while try_count > 0:
            captured_exception = None
            try:
                campaign_id = campaign.campaign_id
                now = datetime.now()


                url = f"https://eu1.dashboard.clevertap.com/{os.getenv('CT_ACC_ID')}/campaigns/campaign/{campaign_id}/report/overview"

                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Android Settings')]"))
                )

                sleep(2)

                android_settings_tab = driver.find_element(By.XPATH, "//*[contains(text(), 'Android Settings')]")
                driver.execute_script("arguments[0].click();", android_settings_tab)

                sleep(1)

                ios_metadata = {}
                ios_key_value_pairs = driver.find_elements(By.XPATH, "//div[@ios]//*[contains(text(), 'Custom key-value pairs')]/following-sibling::span")

                for pair in ios_key_value_pairs:
                    pair = driver.execute_script("return arguments[0].childNodes[0].nodeValue.trim();", pair)

                    key, value = pair.split(" - ", 1)
                    ios_metadata[key.strip()] = value.strip()

                ios_settings_tab = driver.find_element(By.XPATH, "//*[contains(text(), 'iOS Settings')]")
                driver.execute_script("arguments[0].click();", ios_settings_tab)

                sleep(1)

                android_metadata = {}
                android_key_value_pairs = driver.find_elements(By.XPATH, "//div[@android]//*[contains(text(), 'Custom key-value pairs')]/following-sibling::span")

                for pair in android_key_value_pairs:
                    pair = driver.execute_script("return arguments[0].childNodes[0].nodeValue.trim();", pair)

                    key, value = pair.split(" - ", 1)
                    android_metadata[key.strip()] = value.strip()

                is_valid, validation_message = validate_metadata_for_ios_and_android(android_metadata, ios_metadata, campaign.name)
                if is_valid:
                    campaign.custom_metadata = {"ios": ios_metadata, "android": android_metadata}

                    if "url" in ios_metadata:
                        is_valid, validation_message = validate_link_domain(ios_metadata["url"])
                        if is_valid:
                            link_validator_factory = LinkValidatorFactory.get_link_validator(ios_metadata["url"])
                            is_valid, validation_message = link_validator_factory.validate()

                campaign.validation_notes = validation_message
                break
            except Exception as e:
                try_count -= 1
                captured_exception = e

        if try_count == 0 and captured_exception is not None:
            print(f"Exception occurred while getting metadata of campaign : {campaign.campaign_id}, err: {captured_exception}")
            campaign.validation_notes = "Some error occurred while validating this campaign metadata, pls check with the team"
            # raise captured_exception # should not break the time schedule script incase this validation fails; instead send some generic error in the sheet

        print(f'time taken by get_campaign_metadata: {datetime.now() - now}')

    return campaigns


def get_campaign_user_base(driver, campaigns):
    for campaign in campaigns:
        try_count = 2
        captured_exception = None

        while try_count > 0:
            captured_exception = None
            try:
                campaign_id = campaign.campaign_id
                now = datetime.now()

                url = f"https://eu1.dashboard.clevertap.com/{os.getenv('CT_ACC_ID')}/campaigns/campaign/{campaign_id}/edit"

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

                break
            except Exception as e:
                try_count -= 1
                captured_exception = e

        if try_count == 0 and captured_exception is not None:
            print(f"Exception occurred while getting userbase of campaign : {campaign.campaign_id}")
            raise captured_exception

        print(f'time taken by get_user_base: {datetime.now() - now}')

    return campaigns

def stop_campaign(driver):
    return # TODO: UPDATE THIS CODE

def update_scheduled_time(driver, campaign_schedules):
    campaign_update_status = {}

    for campaign in campaign_schedules:
        try:
            if campaign.schedule_time_notes == constants.EXCEEDED_ALIGNED_LIMIT:
                stop_campaign(driver)
                return

            if campaign.preferred_schedule_time is None or campaign.preferred_schedule_time == campaign.original_schedule_time:
                continue

            driver.get(f"https://eu1.dashboard.clevertap.com/{os.getenv('CT_ACC_ID')}/campaigns/campaign/{campaign.campaign_id}/edit")

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

            sleep(100) # TODO: ADDED FOR TESTING; TO REMOVE ONCE DONE
            time_submit_btn = driver.find_element(By.XPATH,"//span[text()='Done']")
            time_submit_btn.click()

            sleep(1)
            submit_btn = driver.find_element(By.XPATH,"//span[text()='All Done!']//following-sibling::*/following-sibling::*")
            submit_btn.click()

            submit_btn = driver.find_element(By.XPATH,"/html/body/div[3]/div[3]/div/div/div[2]/button[1]")
            submit_btn.click()

            sleep(3)

            if True: # TODO: TO UPDATE
                campaign_update_status[campaign.campaign_id] = 'UPDATED'
            else:
                campaign_update_status[campaign.campaign_id] = 'NOT_UPDATED'
        except Exception as e:
            print(f'ERROR - {e}')
            campaign_update_status[campaign.campaign_id] = str(e)


    return campaign_update_status