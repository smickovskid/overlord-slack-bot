from flask import Flask
from threading import Thread
from utils.routes import Routes
from utils.slack_bot import Slack
import os
import schedule
import time
app = Flask(__name__)


channel_id = "C04RH4ZBK5X"

slack = Slack()
routes = Routes(app, slack)


def send_daily_question(test=False):
    today = time.strftime("%d/%m/%Y")
    question = f"Fill out your daily update - {today}"
    slack.send_question_to_users(question, channel_id)


def schedule_daily_question():
    daily_when = "09:06"
    schedule.every().monday.at(daily_when).do(send_daily_question)
    schedule.every().tuesday.at(daily_when).do(send_daily_question)
    schedule.every().wednesday.at(daily_when).do(send_daily_question)
    schedule.every().thursday.at(daily_when).do(send_daily_question)
    schedule.every().friday.at(daily_when).do(send_daily_question)
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_app():
    app.run(port=5500)


if __name__ == "__main__":
    Thread(target=schedule_daily_question).start()
    Thread(target=start_app).start()
