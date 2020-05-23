import os
import logging
from flask import Flask, request, make_response, render_template
from slack import WebClient
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from quarantine_tracker import GotItMessage
from flask_socketio import SocketIO

app = Flask(__name__)
SocketIO(app, cors_allowed_origins='*')
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)


def _event_handler(event_type, slack_event):
    print(slack_event)
    team_id = slack_event['team_id']

    if event_type == 'app_mention':
        ts = slack_event['event']['ts']

        response = slack_web_client.chat_postMessage(
            channel = 'C013ZC50SPQ',
            text = f'You mentioned me directly at timestamp {ts}'
        )
        return make_response('Got the mention', 200,)

@app.route('/', methods = ['GET', 'POST'])
def process_request():
    slack_event = request.get_json()

    if 'challenge' in slack_event:
        return make_response(slack_event['challenge'], 200, {'content_type': 'application/json'})

    if 'event' in slack_event:
        event_type = slack_event['event']['type']

        return _event_handler(event_type, slack_event)




if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
