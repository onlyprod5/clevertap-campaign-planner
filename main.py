from datetime import datetime
from dotenv import load_dotenv
from datetime import timedelta
from time import sleep

from schedule_computer import compute_best_schedule
from api_helper import fetch_campaigns
from selenium_helper import setup_browser, quit_browser, get_user_base, update_scheduled_time, login
from slack_helper import send_message


MAX_LIMIT=1500000

load_dotenv()

now = datetime.now().replace(minute=0, second=0, microsecond=0)

print(f"started-{now}")

st_time = now + timedelta(hours=1)
end_time = st_time + timedelta(hours=1, minutes=-1)

# Step1: Fetch the campaigns from CleverTap API
campaigns = fetch_campaigns(st_time, end_time)

# Step2: Setup browser and login to CleverTap
driver = setup_browser()
login(driver)

# Step3: Get Userbase for all schedules
campaign_info = get_user_base(driver, campaigns)

# Step4: Compute the preferred schedule time for each schedule
campaign_schedules, campaign_notes_dict = compute_best_schedule(campaign_info, MAX_LIMIT, st_time, end_time)

# Step5: Send the preferred schedule time for each schedule on slack
send_message(campaign_schedules, campaign_notes_dict, st_time, end_time)

print(f'first pass: total_time: {datetime.now() - now}')

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
