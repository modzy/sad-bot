# :cry: :robot: Sad Bot

Sad bot is a Slack bot that will respond when mentioned in a [slack](https://slack.com) channel or conversation with a short message. If your message seems very positive, Sad Bot will respond positively. If your message seems negative, then Sad Bot will share an encouraging quote.

## How it's built
Sad bot is very simple and uses just a few technologies to work:
* Python
* Flask
* A [sentiment anlaysis model](https://www.modzy.com/marketplace/model-task/label-or-classify/sentiment-analysis/) hosted by [Modzy](https://www.modzy.com)
* *For local development you can use [ngrok](https://ngrok.com/download) to redirect event information to your localhost*

## Example Slack Conversation with Sad Bot
**My Name** 4:29pm

I'm on top of the world today! `@Sad Bot`

**Sad Bot** `APP` 4:29pm

You seem happy! :smile:

**My Name** 4:30pm

I have a lot of errands to run today `@Sad Bot`

**Sad Bot** `APP` 4:30pm

You seem to be a bit bleh :neutral_face:

How about some coffee :coffee: ?

**My Name** 4:31pm

I'm very very sad `@Sad Bot`

**Sad Bot** `APP` 4:31pm

You seem sad :slightly_frowning_face:

:butterfly: How wonderful it is that nobody need wait a single moment before starting to improve the world.

## Credits
Sad bot is built based on a tutorial by [Saurav Shrivastav](https://github.com/Saurav-Shrivastav)
* Medium Article: [How to build your first slack bot in 2020 with Python & Flask using the Slack Events-API]()
* Slack bot tutorial repo: https://github.com/Saurav-Shrivastav/Slackbot-tutorial
