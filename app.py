import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from quarantine_tracker import GotItMessage
from flask_socketio import SocketIO

app = Flask(__name__)
server = app.server
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

SocketIO(app, cors_allowed_origins='*')

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# App data
members_in: []
members_out: []


@app.route('/')
def hello():
    return 'Hello world!'


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
    print('Got a message')

    return got_it(user_id, channel_id)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
