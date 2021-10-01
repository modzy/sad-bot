from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import os
from threading import Thread
from slack import WebClient
from modzy import ApiClient, error
from modzy._util import file_to_bytes
import numpy as np
import random
import re

# This `app` represents your existing Flask app
app = Flask(__name__)

# Accessing environment variables for athentication
## For Slack
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
slack_token = os.environ['SLACK_BOT_TOKEN']
VERIFICATION_TOKEN = os.environ['VERIFICATION_TOKEN']
## For Modzy
API_URL = "https://app.modzy.com/api"
API_KEY = os.environ['MODZY_API_KEY']

# Instantiating slack client and modzy client
slack_client = WebClient(slack_token)
modzy_client = ApiClient(base_url=API_URL, api_key=API_KEY)

# An example of one of your Flask app's routes
@app.route("/")
def event_hook(request):
    json_dict = json.loads(request.body.decode("utf-8"))
    if json_dict["token"] != VERIFICATION_TOKEN:
        return {"status": 403}

    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return response_dict
    return {"status": 500}
    return

# Sets up your bot to listen for slack events at /slack/events
## Note: Don't forget to add "/slack/events" to the end of the https URL you
## get from ngrok before adding it as the Request URL for your Event Subscription
## in Slack
slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)  

# Handling the data when our bot mentioned
@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    def send_reply(value):
        event_data = value
        message = event_data["event"]
        if message.get("subtype") is None:
            command = message.get("text")
            channel_id = message["channel"]
            # Creates the message our bot will reply with
            message = custom_message(
                # Removes the name of the bot with a bit of regex so that it's not included in the sentiment scoring
                sentiment_score(re.sub('^<@[A-Z0-9]*>', '', command))
                )
            slack_client.chat_postMessage(channel=channel_id, text=message)
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)


# Running sentiment analysis on the message our bot recieved
def sentiment_score(raw_text):
    sources = {}
    sources[raw_text] ={
        "input.txt": raw_text
    }; 
    # Sends the slack message to a sentiment analysis model hosted by Modzy
    job = modzy_client.jobs.submit_text("ed542963de", "1.0.1", sources, explain=True)
    # Waits until the input has finished processing, then requests the prediction (Modzy is async)
    result = modzy_client.results.block_until_complete(job, timeout=None)
    # Some dictionary stuff to isolate just the negative and positive sentiment scores
    results_json = result.get_first_outputs()['results.json']
    class_predictions = results_json['data']['result']['classPredictions']
    for api_object in class_predictions:
        if api_object['class'] == "positive":
            positive_score = api_object['score']
        elif api_object['class'] == "negative":
            negative_score = api_object['score']
    composite_score = np.divide(np.add(positive_score,np.multiply(negative_score,-1)),2)
    print(composite_score)
    return composite_score


# Custom message based on how happy or sad you seem
def custom_message(sentiment_score):    
    # Ugly way to create an array of random uplifting emoji
    emoji = []
    emoji.append(':heart: ')
    emoji.append(':people_hugging: ')
    emoji.append(':palms_up_together: ')
    emoji.append(':muscle: ')
    emoji.append(':ear: ')
    emoji.append(':woman_in_lotus_position: ')
    emoji.append(':dog: ')
    emoji.append(':cat: ')
    emoji.append(':butterfly: ')
    emoji.append(':sunflower: ')
    emoji.append(':partly_sunny_rain: ')

    # Ugly way to create an array of random uplifting quotes
    encouragement = []
    encouragement.append('Never give up, for that is just the place and time that the tide will turn.')
    encouragement.append('We must embrace pain and burn it as fuel for our journey.')
    encouragement.append('Focus on the journey, not the destination.')
    encouragement.append('Discouragement and failure are two of the surest stepping stones to success.')
    encouragement.append('How wonderful it is that nobody need wait a single moment before starting to improve the world.')
    encouragement.append('Do not let what you cannot do interfere with what you can do.')
    encouragement.append('When we stop opposing reality, action becomes simple, fluid, kind, and fearless.')
    encouragement.append('If there is no struggle, there is no progress.')
    encouragement.append('A ship is always safe at the shore – but that is NOT what it is built for.')
    encouragement.append('The best way to cheer yourself up is to try to cheer somebody else up.')
    encouragement.append('It does not matter how slowly you go as long as you do not stop.')
    encouragement.append('Don’t wait. The time will never be just right.')
    encouragement.append('It always seems impossible until it’s done.')
    
    # Bot composes a message based on how happy or sad the message seems
    if sentiment_score >= 0.05:
        m = (
            "You seem happy! :smile:"
        )
    elif sentiment_score < -0.05:
        m = (
            "You seem sad :slightly_frowning_face: \n" + emoji[random.randrange(len(emoji))] + encouragement[random.randrange(len(encouragement))]
        ) 
    else:
        m = (
            "You seem to be a bit bleh :neutral_face: \n How about some coffee :coffee: ?"
        )
    return m


# Start the server on port 3000
if __name__ == "__main__":
  app.run(port=3000)