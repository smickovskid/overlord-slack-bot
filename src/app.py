from flask import Flask
from threading import Thread
from utils.routes import Routes
from utils.slack_bot import Slack
import schedule
import time
from os import environ
app = Flask(__name__)


DEBUG = environ.get('DEBUG')

channel_id = "C056H1LM9NU"
if DEBUG is not None:
    channel_id = "C04RH4ZBK5X"

slack = Slack()
routes = Routes(app, slack)


def send_daily_question():
    today = time.strftime("%d/%m/%Y")
    question = f"Fill out your daily update - {today}"
    slack.send_question_to_users(question, channel_id)


def schedule_daily_question():
    daily_when = "15:30"
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
    if environ.get('DEBUG') is not None:
        print("DEBUG MODE")
        send_daily_question()
    Thread(target=schedule_daily_question).start()
    Thread(target=start_app).start()
