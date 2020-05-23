class GotItMessage:
    # Let users know that their checkin/checkout has been received

    leaving_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Got it, marking you down as leaving"
        }
    }

    def __init__(self, channel, leaving = True):
        self.channel = channel
        self.username = "Quarantine"
        self.leaving = leaving

    def get_message_payload(self):
        return {
            "channel": self.channel,
            "username": self.username,
            "blocks": [
                self.leaving_block
            ]
        }
