#!/usr/bin/env python3

import smtplib, ssl
import praw
import os
from collections import defaultdict
from discord_webhook import DiscordWebhook, DiscordEmbed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Sets up the Reddit praw API
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
user_agent = os.environ['USER_AGENT']
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

#Gets deals from /r/deals
deals = defaultdict(list)
for submission in reddit.subreddit("deals").top("day"):
  deals[submission.title] = "https://reddit.com" + submission.permalink

#Gets deals from /r/eFreebies
freebies = defaultdict(list)
for submission in reddit.subreddit("eFreebies").top("day"):
  freebies[submission.title] = "https://reddit.com" + submission.permalink

#Gets deals from /r/GameDeals
gameDeals = defaultdict(list)
for submission in reddit.subreddit("GameDeals").top("day"):
  gameDeals[submission.title] = "https://reddit.com" + submission.permalink

#Email Configuration
port = 465
smtp_server = "smtp.gmail.com"
sender_email = os.environ['EMAIL']
sender_password = os.environ['EMAIL_PASSWORD']

#Gets all recipients
receiver_emails = []
for email in open(os.environ['RECIPIENT_LIST']):
  receiver_emails.append(email.strip())

#Formates email
message = MIMEMultipart("alternative")
message["Subject"] = "Today's Deals and Freebies"
message["From"] = sender_email
message["To"] = sender_email

html_body = """\
<html>
  <body>
    <h2>
      Today's top deals from r/deals
    </h2>
    <p>
      {}
    </p>
    <br>
    <h2>
      Today's top deals from r/GameDeals
    </h2>
    <p>
      {}
    </p>
    <br>
    <h2>
      Today's top freebies from r/eFreebies
    </h2>
    <p>
      {}
    </p>
  </body>
</html>
"""
#Text for emails
link = "<li><a href=\"{}\">{}</a></li>"
deal_text = ""
gamedeal_text = ""
freeby_text = ""

#Text for webhooks
value_text = "[{}]({})"

#Sets up webhooks
webhook_deals = DiscordWebhook(url=os.environ["DISCORD_WEBHOOK"])
webhook_gamedeals = DiscordWebhook(url=os.environ["DISCORD_WEBHOOK"])
webhook_freebies = DiscordWebhook(url=os.environ["DISCORD_WEBHOOK"])

#Sets up embeds for webhooks
embed_deals = DiscordEmbed(title="Today's top deals from r/deals", color=15844367)
embed_gamedeals = DiscordEmbed(title="Today's top deals from r/GameDeals", color=15844367)
embed_freebies = DiscordEmbed(title="Todays top freebies from r/eFreebies", color=15844367)

#Adds deals
dealCounter = 1
if len(deals) > 0:
  for title, url in deals.items():
    deal_text += link.format(url,title)
    embed_deals.add_embed_field(name=dealCounter, value=value_text.format(title,url))
    dealCounter+=1
else:
  deal_text += "Nothing here today!"
  embed_deals.add_embed_field(name="Nothing here today!")

#Adds game deals
gameDealCounter = 1
if len(gameDeals) > 0:
  for title, url in gameDeals.items():
    gamedeal_text += link.format(url,title)
    embed_gamedeals.add_embed_field(name=gameDealCounter, value=value_text.format(title,url))
    gameDealCounter += 1
else:
  gamedeal_text += "Nothing here today!"
  embed_gamedeals.add_embed_field(name="Nothing here today!")

#Adds freebies
freebieCounter = 1
if len(freebies) > 0:
  for title, url in freebies.items():
    freeby_text += link.format(url,title)
    embed_freebies.add_embed_field(name=freebieCounter, value=value_text.format(title,url))
    freebieCounter+=1
else:
  freeby_text += "Nothing here today!"
  embed_freebies.add_embed_field(name="Nothing here today!")

#Attaches deals to the email
html = html_body.format(deal_text, gamedeal_text, freeby_text)
message.attach(MIMEText(html, "html"))

#Sends email
context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
  server.login(sender_email, sender_password)
  #server.sendmail(sender_email, receiver_emails, message.as_string())

#Adds embeds to webhooks
webhook_deals.add_embed(embed_deals)
webhook_gamedeals.add_embed(embed_gamedeals)
webhook_freebies.add_embed(embed_freebies)

#Executes webhooks
webhook_deals.execute()
webhook_gamedeals.execute()
webhook_freebies.execute()
