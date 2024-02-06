import slack
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import re

#loads the environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#loading hr variables
hr_keywords_str = os.environ.get('hr_keywords')
hr_keywords = hr_keywords_str.split(',')

# Load HR Assignment dictionary from environment variable
hr_assignment_str = os.environ.get('HR_ASSIGNMENT', '{}')
hr_assignment = json.loads(hr_assignment_str)

#loading no no words variables
no_no_words_str = os.environ.get('no_no_words')
no_no_words = no_no_words_str.split(',')

#loading flask and slack adapter
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['signing_secret'],'/slack/events',app)

#defining variables for api
bot_client = slack.WebClient(token=os.environ['slack_token'])
user_client = slack.WebClient(token=os.environ['user_token'])
bot_id = bot_client.api_call('auth.test')['user_id']

pattern_nono = r'\b(?:{})\b'.format('|'.join(map(re.escape, no_no_words)))
pattern_hr = r'\b(?:{}|401k)\b'.format('|'.join(map(re.escape, hr_keywords)))

#when message received, run loop
@slack_event_adapter.on('message')

#defining payload and message being received.  begins the check for keywords and user authentication

def message(payload):
    try:
        event = payload.get('event', {})
        channel_id = event.get('channel')
        user_id = event.get('user')
        text = event.get('text')
        timestamp = event.get('ts')
        user_info = bot_client.users_info(user=user_id)
        real_name = user_info.data.get('user', {}).get('profile', {}).get('real_name')
        #if the a user who is not the bot posts a message
        if bot_id != user_id:
            if re.search(pattern_nono, text.lower()):
                matched_keyword = re.search(pattern_nono, text.lower()).group(0)
                user_client.chat_delete(channel=channel_id,ts=timestamp)
                bot_client.chat_postMessage(channel='C04Q754PE6B',text=('<!here> \n\nUsername: {} \nUser ID: {} \nChannel Name: {} \nMessage: {} \nTime Stamp: {}'.format(real_name, user_id,channel_id, text,timestamp)))
                bot_client.chat_postMessage(channel=user_id,text='Dear {}, \n\nYou have violated the FBIN Connected Slack Guidelines.  Your message containing the violation has been removed from the channel and forwarded for review.  If you have any further questions, please contact your local HRBP'.format(real_name))
                return None
            #checks for any hr related key words
            if re.search(pattern_hr, text.lower()):
                matched_hr_keyword = re.search(pattern_hr, text.lower()).group(0)
                bot_client.chat_postMessage(channel=channel_id,text=('To find out about {} and more relating to HR Services please visit https://fb-frontdoor.com/site/ad9a54e8-01c8-4ed4-8eff-8ef2ba976e2d/dashboard'.format(matched_hr_keyword)))
                # user_name = None
                # for name, data in hr_assignment.items():
                #     if data.get('name') == real_name:
                #         user_name = name
                #         break
                # if user_name:    
                #     hr_rep_data = hr_assignment.get(user_name, {})
                #     hr_rep_name = hr_rep_data.get("hr_rep", "Unknown HR Representative")
                #     hr_rep_email = hr_rep_data.get("email", "Unknown HR Representative Email")
                #     bot_client.chat_postMessage(channel=channel_id, text=f"{user_name}'s HR Representative: {hr_rep_name} ({hr_rep_email})")
                # else:
                #     bot_client.chat_postMessage(channel=channel_id, text="User not found in HR Assignment")
    except:
        return None

if __name__ == '__main__':
    app.run(debug=True)
