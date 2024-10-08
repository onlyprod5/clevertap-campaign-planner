from typing import List
from datetime import datetime
import requests
import os

from campaign import Campaign, CampaignBuilder

def fetch_campaigns(st_time, end_time):
    api_url = "https://api.clevertap.com/1/message/report.json"

    formatted_time = st_time.strftime("%Y%m%d")

    payload = {
        "from": formatted_time,
        "to": formatted_time,
        "status": [ "scheduled" ]
    }

    headers = {
        "Content-Type": "application/json",
        "X-CleverTap-Account-Id": os.getenv('CT_ACC_ID'),
        "X-CleverTap-Passcode": os.getenv('CT_PASS')
    }

    campaigns: List[Campaign] = []

    try_count = 3
    while try_count > 0:
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()

                for campaign in data.get('messages', []):
                    campaign_time = datetime.strptime(campaign['start_date'], "%d %b, %Y %H:%M:%S")

                    if st_time <= campaign_time <= end_time:
                        campaigns.append(
                            CampaignBuilder().
                            set_campaign_id(campaign['message id']).
                            set_original_schedule_time(campaign_time).
                            set_channel(campaign['channel'].lower()).
                            build()
                        )

                break
            else:
                print(f"Failed to fetch campaigns. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                try_count = try_count - 1
                continue
        except Exception as e:
            print(f'exception occurred while calling ct api- {e}')
            try_count = try_count - 1
            continue

    if try_count == 0:
        raise 'exception occurred while calling ct api'

    print("Campaigns in the time frame")
    for campaign in campaigns:
        print(campaign)

    return campaigns
