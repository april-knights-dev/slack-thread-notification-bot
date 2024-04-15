# main.py
import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN
from slackbot import SlackBot

app = App(token=SLACK_BOT_TOKEN)
slackbot = SlackBot(app)

@app.event("app_mention")
def handle_app_mention_events(body, say):
    slackbot.handle_app_mention(body, say)

@app.event("message")
def handle_message_events(body):
    slackbot.handle_message(body)

@app.command("/thread_settings")
def handle_thread_settings_command(ack, body, client):
    ack()
    slackbot.open_settings_modal(client, body)

@app.view("thread_settings_view")
def handle_thread_settings_view_submission(ack, body, client, view):
    ack()
    slackbot.update_thread_settings(client, body, view)

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()