import os
from slack import WebClient

# Initialize the Slack WebClient
slack_client = WebClient(token=os.environ['{place token here for bot}'])

# Get a list of all public channels
response = slack_client.conversations_list(types="public_channel")

# Extract channel IDs from the response
channel_ids = [channel['id'] for channel in response['channels']]

# Bot user ID
bot_user_id = slack_client.auth_test()['user_id']

# Invite the bot to each channel
for channel_id in channel_ids:
    slack_client.conversations_invite(channel=channel_id, users=bot_user_id)
