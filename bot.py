import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

client = slack.WebClient(token=os.environ['slack_token'])

client.chat_postMessage(channel='#it-test-channel',text='This is a test message from Jarvis')