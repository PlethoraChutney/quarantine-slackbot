import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from quarantine_tracker import GotItMessage

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# App data
members_in: []
members_out: []


def got_it(user_id: str, channel: str):

    got_it = GotItMessage(channel)

    message = got_it.get_message_payload()

    slack_web_client.chat_postMessage(**message)


@slack_events_adapter.on("message")
def message(payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if text and text.lower() == "hello":
        return got_it(user_id, channel_id)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)

    import ssl as ssl_lib
    import certifi

    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
