import os
from slack_sdk import WebClient


class Slack:
    def __init__(self, slack_token):
        self.slack_token = slack_token
        self.client = WebClient(self.slack_token)
        self.user_questions = {}

    def get_channel_members(self, channel=None):
        response = self.client.conversations_members(channel=channel)
        return response['members']

    def send_question_to_users(self, question, channel=None):
        users = self.get_channel_members(channel)
        trigger_block = self.create_trigger_block(question)
        input_block = self.create_input_block()

        for user in ["U0179K6LE3A"]:
            user_info = self.client.users_info(user=user)
            if user_info["user"]["is_bot"]:
                continue
            if user != self.client.auth_test()['user_id']:
                response = self.client.conversations_open(users=[user])
                dm_channel = response['channel']['id']
                self.client.chat_postMessage(
                    channel=dm_channel, text=question, blocks=trigger_block)
                self.user_questions[user] = {
                    "dm_channel": dm_channel,
                    "question": {
                        "stage": 1,
                        "text": question
                    },
                    "input_block": input_block
                }

    def create_trigger_block(self, question):
        return [
            {
                "type": "section",
                "block_id": "question",
                "text": {
                    "type": "mrkdwn",
                    "text": question
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Answer"
                    },
                    "action_id": "open_modal"
                }
            }
        ]

    def create_input_block(self):
        return [
            {
                "type": "input",
                "block_id": "automation_count",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "input_text"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter the number of automated test cases you have written today"
                }
            },
            {
                "type": "input",
                "multiline": True,
                "block_id": "automation_reason",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "input_text"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Explain the reason on why you have not automated at least 1 test case"
                }
            }
        ]

    def create_modal_view(self, input_block):
        return {
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

    def handle_user_response(self, user, answer):
        user_question_info = self.user_questions.get(user)

        if user_question_info is None:
            return None, False

        print(user_question_info)
