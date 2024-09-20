import os
import csv
from datetime import datetime

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from campaign import CampaignBuilder

file_path = 'campaigns.csv'
channel_id = 'C07MPL2QFKR'

def send_message(campaigns, campaign_notes, st_time, end_time):
    slack_token = os.getenv('SLACK_TOKEN')
    client = WebClient(token=slack_token)

    if len(campaigns) == 0:
        try:
            response = client.chat_postMessage(
                channel=channel_id,
                text=f"ℹ️ No campaigns were found between {st_time.strftime('%d %b %Y %I:%M%p')} and {end_time.strftime('%d %b %Y %I:%M%p')}"
            )
            print(response)
        except SlackApiError as e:
            print(f"Error sending slack message: {e.response}")
    else:
        write_campaigns_to_csv(campaigns, campaign_notes)
        try:
            response = client.files_upload_v2(
                channel=channel_id,
                file=file_path,
                title="📅 Upcoming Campaign Schedule",
                initial_comment=f"🌟 Here are the campaign details which were scheduled between {st_time.strftime('%d %b %Y %I:%M%p')} and {end_time.strftime('%d %b %Y %I:%M%p')}, along with our suggested timings"
            )
            print(response)
        except SlackApiError as e:
            print(f"Error sending slack message: {e.response}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"CSV file {file_path} deleted.")


def write_campaigns_to_csv(campaigns, campaign_notes):
    header = ['Campaign ID', 'Total Audience', 'Throttle / 5mins', 'Original Schedule Time', 'Preferred Schedule Time', 'Notes']

    # Open the file in write mode
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(header)

        # Write campaign data rows
        for campaign in campaigns:
            writer.writerow([
                campaign.campaign_id,
                campaign.total_audience,
                campaign.throttle,
                campaign.original_schedule_time,
                campaign.preferred_schedule_time,
                campaign_notes[campaign.campaign_id]
            ])

if __name__ == '__main__':
    send_message([CampaignBuilder().
                set_campaign_id('1').
                set_original_schedule_time(datetime.strptime("20 Sep, 2024 12:55:00", "%d %b, %Y %H:%M:%S")).
                set_total_audience(1200000).
                set_throttle(1300000).build()])
