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

def who_in_lab():
    if in_lab:
        present_members = ', '.join(in_lab)
    else:
        present_members = 'Nobody'

    return f'Here\'s who\'s in lab: {present_members}'

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
            user_name = f'<@{user_id}>'
            if 'who' in message_text:
                response = slack_web_client.chat_postMessage(
                    channel = 'C013ZC50SPQ',
                    text = who_in_lab()
                )
            elif ' in' in message_text:
                if user_name not in in_lab:
                    in_lab.append(user_name)

                    response = slack_web_client.chat_postMessage(
                        channel = 'C013ZC50SPQ',
                        text = f'Got it, checking you in.\n{who_in_lab()}'
                    )
                else:
                    response = slack_web_client.chat_postMessage(
                        channel = 'C013ZC50SPQ',
                        text = f'I already had you as present, {user_name}'
                    )
            elif ' out' in message_text:
                if user_name in in_lab:
                    in_lab.remove(user_name)

                    response = slack_web_client.chat_postMessage(
                        channel = 'C013ZC50SPQ',
                        text = f'Hope you got some good work done\n{who_in_lab()}'
                    )
                else:
                    response = slack_web_client.chat_postMessage(
                        channel = 'C013ZC50SPQ',
                        text = f'Can\'t check out if you never came in, {user_name}'
                    )

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
