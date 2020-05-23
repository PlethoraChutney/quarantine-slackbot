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


in_lab = []
out_lab = []

def who_in_lab():
    if in_lab:
        present_members = ', '.join(in_lab)
    else:
        present_members = 'Nobody'
    if out_lab:
        home_members = ', '.join(out_lab)
    else:
        home_members = 'Nobody'

    return f'Here\'s who\'s in lab: {present_members}\nHere\'s who\'s home: {home_members}'

def _event_handler(event_type, slack_event):
    print(slack_event)
    team_id = slack_event['team_id']

    if event_type == 'app_mention':
        ts = slack_event['event']['ts']
        message_tail = slack_event['event']['text'][:-10]

        response = slack_web_client.chat_postMessage(
            channel = 'C013ZC50SPQ',
            text = f'I\'m responding to the message that ended "{message_tail}"'
        )
        return make_response('Got the mention', 200,)

    elif event_type == 'message':
        if slack_event['event']['user'] != 'U014JNM89RP':
            message_text = slack_event['event']['text'].lower()
            user_id = slack_event['event']['user']
            if 'who' in message_text:
                response = slack_web_client.chat_postMessage(
                    channel = 'C013ZC50SPQ',
                    text = who_in_lab()
                )
            else:
                try:
                    payload = {'token': os.environ['SLACK_BOT_TOKEN'], 'user': user_id}
                    slack_web_client.users_identity

                    user_name = r['user']['name']
                    in_lab.append(user_name)
                    print(in_lab)

                    response = slack_web_client.chat_postMessage(
                        channel = 'C013ZC50SPQ',
                        text = f'Got it, checking you in {user_name}'
                    )
                except:
                    pass

        return make_response('Read a message', 200, )

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
