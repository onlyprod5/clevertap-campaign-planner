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
                        build()
                    )
    else:
        print(f"Failed to fetch campaigns. Status code: {response.status_code}")
        print(f"Response: {response.text}")

    print("Campaigns in the time frame")
    for campaign in campaigns:
        print(campaign)

    return campaigns
