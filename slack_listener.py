import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.action("approve_campaign_schedule_action")
def handle_button_click(ack, body, say, client):
    ack()

    original_message_ts = body['container']['message_ts']
    channel_id = body['channel']['id']

    client.chat_postMessage(
        text='',
        blocks=[
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f":heavy_check_mark: Approved by <@{body['user']['id']}>!"
                    }
                ]
            },
        ],
        channel=channel_id,
        thread_ts=original_message_ts
    )

# Start the app using socket mode
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
