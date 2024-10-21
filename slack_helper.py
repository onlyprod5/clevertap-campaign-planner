import json
import os
import csv
from time import sleep

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

file_path = 'campaigns.csv'

def send_message(campaigns, campaign_notes, st_time, end_time):
    slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
    channel_id = os.getenv('SLACK_CHANNEL_ID')

    client = WebClient(token=slack_bot_token)

    if len(campaigns) == 0:
        try:
            client.chat_postMessage(
                channel=channel_id,
                text=f"ℹ️ No campaigns were found between {st_time.strftime('%d %b %Y %I:%M%p')} and {end_time.strftime('%d %b %Y %I:%M%p')}"
            )
        except SlackApiError as e:
            print(f"Error sending slack message: {e.response}")
    else:
        write_campaigns_to_csv(campaigns, campaign_notes)
        try:

            file = client.files_upload_v2(
                channel=channel_id,
                file=file_path,
                title="📅 Upcoming Campaign Schedule",
            )

            sleep(2)

            file_link = file['file']['permalink']

            resp = client.chat_postMessage(
                channel=channel_id,
                blocks= [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":calendar: Upcoming Campaigns Scheduled for the Next Hour :calendar:",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": f":star2: We have campaigns scheduled between {st_time.strftime('%d %b %Y %I:%M%p')} and {end_time.strftime('%d %b %Y %I:%M%p')}. Please review the file for details, including a new suggested time frame.",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"📄 Attached <{file_link}|file>"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "plain_text",
                                "text": "Approve the schedule?",
                                "emoji": True
                            }
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": ":heavy_check_mark: Approve",
                                    "emoji": True
                                },
                                "style": "primary",
                                "value": "approve_campaign_schedule_action",
                                "action_id": "approve_campaign_schedule_action"
                            }
                        ]
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "plain_text",
                                "text": "🔄 Note: If not approved within the next 15 mins, the campaigns will be auto-rescheduled[**Auto-rescheduling is NOT LIVE yet].",
                                "emoji": True
                            }
                        ]
                    }
                ]
            )
        except SlackApiError as e:
            print(f"Error sending the campaign schedule message: {e.response['error']}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

def write_campaigns_to_csv(campaigns, campaign_notes):
    header = ['Campaign ID', 'Campaign Name', 'Total Audience', 'Channel', 'Throttle / 5mins', 'Original Schedule Time', 'Preferred Schedule Time', 'Notes']

    # Open the file in write mode
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(header)

        for campaign in campaigns:
            writer.writerow([
                campaign.campaign_id,
                campaign.name,
                campaign.total_audience,
                campaign.channel,
                campaign.throttle,
                campaign.original_schedule_time,
                campaign.preferred_schedule_time,
                campaign_notes[campaign.campaign_id]
            ])
