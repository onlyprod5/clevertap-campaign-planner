from datetime import datetime
from dotenv import load_dotenv
from datetime import timedelta
from time import sleep

import constants
from schedule_computer import compute_best_schedule
from api_helper import fetch_campaigns, send_script_success_log_to_newrelic
from selenium_helper import setup_browser, quit_browser, get_campaign_user_base, update_scheduled_time, login, get_campaign_metadata
from slack_helper import send_message


def get_current_time():
    return datetime.now().replace(second=0, microsecond=0)


def get_st_and_end_time_schedule(time):
    time_hour = time.strftime("%H")

    for start, end in constants.SCHEDULES:
        start_hour = datetime.strptime(start, "%H:%M").time().strftime("%H")
        if start_hour == time_hour:
            return start, end

    return None, None


def get_schedule_window(time):
    st_time, end_time = get_st_and_end_time_schedule(time)
    if st_time is None or end_time is None:
        print(f"No schedule found for hour of {time}")
        return None, None

    st_time = datetime.combine(time.date(), datetime.strptime(st_time, "%H:%M").time())
    end_time = datetime.combine(time.date(), datetime.strptime(end_time, "%H:%M").time())

    return st_time, end_time


def setup_and_login_browser():
    driver = setup_browser()
    login(driver)
    return driver


def get_campaign_info(driver, campaigns):
    campaigns = get_campaign_user_base(driver, campaigns)
    campaigns = get_campaign_metadata(driver, campaigns)

    return campaigns


def process_campaigns():
    max_limit=1500000
    max_limit_interval_minutes=5

    load_dotenv()

    now = get_current_time()

    print(f"started-{now}")

    time_delta = now + timedelta(hours=1)

    # Step 1: Determine schedule window
    st_time, end_time = get_schedule_window(time_delta)
    if st_time is None or end_time is None:
        send_script_success_log_to_newrelic()
        return

    # Step 2: Fetch the campaigns from CleverTap API
    campaigns = fetch_campaigns(st_time, end_time)

    # Step 3: Setup browser and login to CleverTap
    driver = setup_and_login_browser()

    # Step 4: Get relevant campaign details from ui for all campaigns
    campaign_info = get_campaign_info(driver, campaigns)

    # Step 5: Compute the preferred schedule time for campaigns
    campaign_schedules = compute_best_schedule(campaign_info, max_limit, max_limit_interval_minutes, st_time, end_time)

    # Step 6: Send the preferred schedule times on slack
    send_message(campaign_schedules, st_time, end_time)

    print(f'first pass: total_time: {datetime.now() - now}')

    # Step 7: Send script success log to newrelic
    send_script_success_log_to_newrelic()

    # if len(campaign_schedules) != 0:
        # Step6: Sleep for some 15-20 minutes & then update the schedule.
        # sleep(15*60)

        # now = datetime.now()
        # campaign_update_status = update_scheduled_time(driver, campaign_schedules)

        # Step7: update the schedule time for each schedule
        # send_message(campaign_schedules, campaign_update_status, st_time, end_time)
        # print(f'final update: total_time: {datetime.now() - now}')

    # Quit browser
    quit_browser(driver)


if __name__ == "__main__":
    process_campaigns()