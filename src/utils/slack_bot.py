import os
from slack_sdk import WebClient


class Slack:
    def __init__(self, slack_token, channel_id):
        self.slack_token = slack_token
        self.client = WebClient(self.slack_token)
        self.channel_id = channel_id
        self.user_questions = {}

    def get_channel_members(self):
        response = self.client.conversations_members(channel=self.channel_id)
        return response['members']

    def send_question_to_users(self, question):
        users = self.get_channel_members()
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
                    channel=dm_channel, text="asdas", blocks=trigger_block)
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
                "block_id": "user_input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "input_text"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Your answer"
                }
            }
        ]

    def handle_user_response(self, user, answer):
        user_question_info = self.user_questions.get(user)

        if user_question_info is None:
            return None, False

        user_question_stage = user_question_info["stage"]
        if user_question_stage == 1:
            if answer.isdigit() and int(answer) == 0:
                next_question = "Please explain why you haven't automated any tests today"
                self.user_questions[user]["stage"] = 2
                return next_question, False
            else:
                result = f"<@{user}> automated {answer} tests today."
                self.user_questions.pop(user)
                return result, True
        elif user_question_stage == 2:
            result = f"<@{user}> hasn't automated any tests today because: {answer}"
            self.user_questions.pop(user)
            return result, True
