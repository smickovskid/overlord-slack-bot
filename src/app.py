from flask import Flask
from threading import Thread
from utils.routes import Routes
from utils.slack_bot import Slack
import os

app = Flask(__name__)

slack_token = os.environ['SLACK_BOT_TOKEN']
channel_id = "C04RH4ZBK5X"

slack = Slack(slack_token, channel_id)
routes = Routes(app, slack)


def start_app():
    question = "How many automated test cases did you write today?"
    slack.send_question_to_users(question)
    app.run(port=5500)


if __name__ == "__main__":
    Thread(target=start_app).start()
