# routes.py

from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter
from .slack_bot import Slack
from threading import Thread
import json
import os

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
VERIFICATION_TOKEN = os.environ['SLACK_SIGNING_SECRET']

slack_token = os.environ['SLACK_BOT_TOKEN']
channel_id = "C04RH4ZBK5X"

slack = Slack(slack_token, channel_id)

greetings = ["hi", "hello", "hello there", "hey"]


class Routes:
    def __init__(self, app, slack):
        self.app = app
        self.slack = slack
        self.slack_events_adapter = SlackEventAdapter(
            SLACK_SIGNING_SECRET, "/slack/events", app)

        @self.slack_events_adapter.on("app_mention")
        def handle_message(event_data):
            def send_reply(value):
                event_data = value
                message = event_data["event"]
                if message.get("subtype") is None:
                    command = message.get("text")
                    user = message["user"]

                    if user in self.slack.user_questions:
                        response, post_in_channel = self.slack.handle_user_response(
                            user, command)
                        if post_in_channel:
                            self.slack.client.chat_postMessage(
                                channel=channel_id, text=response)
                        else:
                            dm_channel = message["channel"]
                            self.slack.client.chat_postMessage(
                                channel=dm_channel, text=response)
                    else:
                        channel = message["channel"]
                        if any(item in command.lower() for item in greetings):
                            message = "Hello <@%s>! :tada:" % message["user"]
                            self.slack.client.chat_postMessage(
                                channel=channel, text=message)

            thread = Thread(target=send_reply, kwargs={"value": event_data})
            thread.start()
            return Response(status=200)

        @self.app.route("/")
        def event_hook():
            json_dict = json.loads(request.data.decode("utf-8"))
            if json_dict["token"] != VERIFICATION_TOKEN:
                return {"status": 403}

            if "type" in json_dict:
                if json_dict["type"] == "url_verification":
                    response_dict = {"challenge": json_dict["challenge"]}
                    return response_dict
            return {"status": 500}

        @self.app.route("/slack/interaction", methods=["POST"])
        def handle_interaction():
            payload = json.loads(request.form["payload"])

            if payload["type"] == "block_actions":
                action_id = payload["actions"][0]["action_id"]
                user = payload["user"]["id"]

                if action_id == "open_modal" and user in self.slack.user_questions:
                    trigger_id = payload["trigger_id"]
                    dm_channel = self.slack.user_questions[user]["dm_channel"]
                    input_block = self.slack.user_questions[user]["input_block"]

                    modal_view = {
                        "type": "modal",
                        "callback_id": "submit_modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Your Answer"
                        },
                        "blocks": input_block,
                        "submit": {
                            "type": "plain_text",
                            "text": "Submit"
                        }
                    }

                    self.slack.client.views_open(
                        trigger_id=trigger_id, view=modal_view)

            elif payload["type"] == "view_submission":
                callback_id = payload["view"]["callback_id"]
                user = payload["user"]["id"]

                if callback_id == "submit_modal" and user in self.slack.user_questions:
                    input_value = payload["view"]["state"]["values"]["user_input"]["input_text"]["value"]
                    response, post_in_channel = self.slack.handle_user_response(
                        user, input_value)

                    if post_in_channel:
                        self.slack.client.chat_postMessage(
                            channel=channel_id, text=response)
                    else:
                        print(self.slack.user_questions[user])

            return Response(status=200)


routes = Routes(app, slack)
