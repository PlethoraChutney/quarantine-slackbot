# Quarantine Checkin Manager
## Purpose
For lab reopenings at OHSU, we need to keep track of who's in lab at any given time.
Sending messages to a channel does technically work. However, it's easy to
lose track of who is in or out of lab, and results in users getting a lot of
notifications they don't need.

The purpose of this bot is twofold:
 1. Keep track of who is in lab, and report this information as needed
 2. Reduce unnecessary notifications to users

## Installation
As of right now, making this app publicly distributible is more work than I want
to do. So you'll have to [make your own Slack App](https://api.slack.com), and host this repo
somewhere. I'm using a free [heroku](https://www.heroku.com) account and it works fine. Make
sure to give heroku the two environment variables, `SLACK_BOT_TOKEN` and
`SLACK_SIGNING_SECRET`.

I *highly recommend* installing this app in its own channel
that has *no other use*, since it has very lax grep rules for user messages.

## Usage
### Checking in
When a user sends any message including the characters ` in` (e.g., "Checking in"),
they will be checked in and receive a confirmation message with everyone else
currently in lab tagged.
### Checking out
Similarly, a message including ` out` (e.g., "I'm out") will check the user out,
and tag all remaining members in lab.
### Current members
If the message contains the characters `who`, it will not check anyone in or out,
but instead list all currently-in members. I.e., `Who's in` will list current members,
but not check in the sender.
