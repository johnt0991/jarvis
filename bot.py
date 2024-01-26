import slack
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

#loads the environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#loading hr variables
hr_keywords_str = os.environ.get('hr_keywords')
hr_keywords = hr_keywords_str.split(',')

# Load HR Assignment dictionary from environment variable
hr_assignment_str = os.environ.get('HR_ASSIGNMENT', '{}')
hr_assignment = json.loads(hr_assignment_str)

#loading flask and slack adapter
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['signing_secret'],'/slack/events',app)

#defining variables for api
client = slack.WebClient(token=os.environ['slack_token'])
bot_id = client.api_call('auth.test')['user_id']

#when message received, run loop
@slack_event_adapter.on('message')

#defining payload from messages received
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    user_id = event.get('user')
    text = event.get('text')
    user_info = client.users_info(user=user_id)
    real_name = user_info.data.get('user', {}).get('profile', {}).get('real_name')

    #if the a user who is not the bot posts a message
    if bot_id != user_id:
        print(real_name)
        print(hr_keywords)
        #checks for any hr related key words
        if any(keyword.lower() in text.lower() for keyword in hr_keywords):
            user_name = None
            for name, data in hr_assignment.items():
                if data.get('name') == real_name:
                    user_name = name
                    break
            if user_name:    
                hr_rep_data = hr_assignment.get(user_name, {})
                hr_rep_name = hr_rep_data.get("hr_rep", "Unknown HR Representative")
                hr_rep_email = hr_rep_data.get("email", "Unknown HR Representative Email")
                client.chat_postMessage(channel=channel_id, text=f"{user_name}'s HR Representative: {hr_rep_name} ({hr_rep_email})")
            else:
                client.chat_postMessage(channel=channel_id, text="User not found in HR Assignment")
                return

        else:        
            client.chat_postMessage(channel='#it-test-channel',text="Success: /'else/' variable reached")

if __name__ == '__main__':
    app.run(debug=True)
