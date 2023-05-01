from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter
from .slack_bot import Slack
import json
import os

SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
VERIFICATION_TOKEN = os.environ['SLACK_SIGNING_SECRET']

slack_token = os.environ['SLACK_BOT_TOKEN']

slack = Slack(slack_token)


class Routes:
    def __init__(self, app, slack):
        self.app = app
        self.slack = slack
        self.slack_events_adapter = SlackEventAdapter(
            SLACK_SIGNING_SECRET, "/slack/events", app)

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
                    input_block = self.slack.user_questions[user]["input_block"]

                    modal_view = self.slack.create_modal_view(input_block)

                    self.slack.client.views_open(
                        trigger_id=trigger_id, view=modal_view)

            elif payload["type"] == "view_submission":
                callback_id = payload["view"]["callback_id"]
                user = payload["user"]["id"]

                if callback_id == "submit_modal" and user in self.slack.user_questions:
                    daily_update = payload["view"]["state"]["values"]["daily_update"]["input_text"]["value"]
                    automation_reason = payload["view"]["state"]["values"]["automation_reason"]["input_text"]["value"]
                    blockers = payload["view"]["state"]["values"]["blockers"]["input_text"]["value"]
                    print(daily_update)
                    print(automation_reason)
                    print(blockers)
                    send_status_message = self.slack.send_status_message(
                        user, daily_update)

            return Response(status=200)
