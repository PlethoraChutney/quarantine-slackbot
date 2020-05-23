import os
import logging
from flask import Flask, request, make_response, render_template
from slack import WebClient
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from flask_socketio import SocketIO

app = Flask(__name__)
SocketIO(app, cors_allowed_origins='*')
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

def who_in_lab(workspace):
    if not os.path.exists(workspace):
        os.makedirs(workspace)

    present_members = ', '.join([f'<@{x}>' for x in os.listdir(workspace)])
    if present_members == '':
        present_members = 'nobody'

    return f'Here\'s who\'s in lab: {present_members}'

def check_in(direction, user_name, user_id, workspace):
    if not os.path.exists(workspace):
        os.makedirs(workspace)

    if direction == 'in':
        if os.path.exists(os.path.join(workspace, user_id)):
            return f'I already had you present, {user_name}'
        else:
            open(os.path.join(workspace, user_id), 'a').close()
            return f'Got it, checking you in.\n{who_in_lab()}'
    elif direction == 'out':
        if os.path.exists(os.path.join(workspace, user_id)):
            os.remove(os.path.join(workspace, user_id))
            return f'Hope you got some good work done\n{who_in_lab()}'
        else:
            return f'Can\'t check out if you never came in, {user_name}'

def _event_handler(event_type, slack_event):

    if event_type == 'message':
        if 'bot_id' not in slack_event['event']:
            team_id = slack_event['team_id']
            message_text = slack_event['event']['text'].lower()
            user_id = slack_event['event']['user']
            user_name = f'<@{user_id}>'
            channel = slack_event['event']['channel']
            if 'who' in message_text:
                response = slack_web_client.chat_postMessage(
                    channel = channel,
                    text = who_in_lab(team_id)
                )
            elif ' in' in message_text:
                response = slack_web_client.chat_postMessage(
                    channel = channel,
                    text = check_in('in', user_name, user_id, team_id)
                )
            elif ' out' in message_text:
                response = slack_web_client.chat_postMessage(
                    channel = channel,
                    text = check_in('out', user_name, user_id, team_id)
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
    else:
        return 'Hello world!'




if __name__ == "__main__":
    # logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
