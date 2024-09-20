from datetime import datetime
from dotenv import load_dotenv
from datetime import timedelta


from schedule_computer import compute_best_schedule
from api_helper import fetch_campaigns

from selenium_helper import setup_browser, quit_browser, get_user_base, update_scheduled_time, login
from slack_helper import send_message

MAX_LIMIT=1500000

load_dotenv()

now = datetime.now()

print(f"started-{now}")

# Step1: Fetch the campaigns from CleverTap API
st_time = now + timedelta(hours=1)
end_time = st_time + timedelta(hours=1)

campaigns = fetch_campaigns(st_time, end_time)

# Step2: Setup browser and login to CleverTap
driver = setup_browser()
login(driver)

# Step3: Get Userbase for all schedules
campaign_info = get_user_base(driver, campaigns)

# Step4: Compute the schedule time for each schedule
campaign_schedules, campaign_notes_dict = compute_best_schedule(campaign_info, MAX_LIMIT, st_time, end_time)

# Step5: Update the schedule time for each schedule
# update_scheduled_time(driver, campaign_schedules)
send_message(campaign_schedules, campaign_notes_dict, st_time, end_time)

# Step6: Quit browser
quit_browser(driver)

print(f'total_time: {datetime.now() - now}')
