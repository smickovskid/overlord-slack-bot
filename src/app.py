from flask import Flask
from threading import Thread
from utils.routes import Routes
from utils.slack_bot import Slack
import os
import schedule
import time
app = Flask(__name__)

slack_token = os.environ['SLACK_BOT_TOKEN']
channel_id = "C04RH4ZBK5X"

slack = Slack(slack_token)
routes = Routes(app, slack)


def send_daily_question():
    today = time.strftime("%d/%m/%Y")
    question = f"Daily update - {today}"
    slack.send_question_to_users(question, channel_id)


def schedule_daily_question():
    schedule.every().day.at("19:39").do(send_daily_question)
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_app():
    app.run(port=5500)


if __name__ == "__main__":
    Thread(target=schedule_daily_question).start()
    Thread(target=start_app).start()
