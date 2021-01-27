#!/usr/bin/env python3

import smtplib, ssl
import praw
import environment as env
from collections import defaultdict
from discord_webhook import DiscordWebhook, DiscordEmbed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Sets up the Reddit praw API
reddit = praw.Reddit(client_id=env.CLIENT_ID, client_secret=env.CLIENT_SECRET, user_agent=env.USER_AGENT)

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

#Gets deals from /r/buildapcsales
pcDeals = defaultdict(list)
for submission in reddit.subreddit("buildapcsales").top("day"):
  pcDeals[submission.title] = "https://reddit.com" + submission.permalink

#Formates email
message = MIMEMultipart("alternative")
message["Subject"] = "Today's Deals and Freebies"
message["From"] = env.EMAIL
message["To"] = env.EMAIL

html_body = """\
<html>
  <body>
    <h2> Today's top deals from r/deals </h2>
    <p> {} </p>
    <br>

    <h2> Today's top deals from r/GameDeals </h2>
    <p> {} </p>
    <br>

    <h2> Today's top freebies from r/eFreebies </h2>
    <p> {} </p>
    <br>

    <h2> Today's top deals from r/buildapcsales </h2>
    <p> {} </p>
  </body>
</html>
"""
#Text for emails
link = "<li><a href=\"{}\">{}</a></li>"
deal_text = ""
gamedeal_text = ""
freeby_text = ""
pcdeal_text = ""

#Text for webhooks
value_text = "- [{}](<{}>)\n"
webhook_deal_text = "***Today's top deals from r/deals!***\n>>> "
webhook_gamedeal_text = "***Today's top deals from r/GameDeals!***\n>>> "
webhook_freebies_text = "***Today's top freebies from r/eFreebies!***\n>>> "
webhook_pcdeal_text = "***Today's top deals from r/buildapcsales!***\n>>> "

#For times when there are a lot of posts (2000 character limit of webhook exceeds)
wdText = []
wgdText = []
wfText = []
wpdText = []

#Adds deals
if len(deals) > 0:
  for title, url in deals.items():
    deal_text += link.format(url,title)  
    addDeal = value_text.format(title,url)
    if(len(webhook_deal_text) + len(addDeal) > 2000):
      wdText.append(webhook_deal_text)
      webhook_deal_text = ">>> " + addDeal
    else:
      webhook_deal_text += addDeal
  wdText.append(webhook_deal_text)  
else:
  deal_text += "Nothing here today!"
  webhook_deal_text += "Nothing here today!"
  wdText.append(webhook_deal_text)  

#Adds game deals
if len(gameDeals) > 0:
  for title, url in gameDeals.items():
    gamedeal_text += link.format(url,title)
    addGameDeal = value_text.format(title,url)
    if(len(webhook_gamedeal_text) + len(addGameDeal) > 2000):
      wgdText.append(webhook_gamedeal_text)
      webhook_gamedeal_text = ">>> " + addGameDeal
    else:
      webhook_gamedeal_text += addGameDeal
  wgdText.append(webhook_gamedeal_text) 
else:
  gamedeal_text += "Nothing here today!"
  webhook_gamedeal_text += "Nothing here today!"
  wgdText[0] = webhook_gamedeal_text

#Adds freebies
if len(freebies) > 0:
  for title, url in freebies.items():
    freeby_text += link.format(url,title)
    addFreebie = value_text.format(title,url)
    if(len(webhook_freebies_text) + len(addFreebie) > 2000):
      wfText.append(webhook_freebies_text)
      webhook_freebies_text = ">>> " + addFreebie
    else:
      webhook_freebies_text += addFreebie
  wfText.append(webhook_freebies_text)
else:
  freeby_text += "Nothing here today!"
  webhook_freebies_text += "Nothing here today!"
  wfText[0] = webhook_freebies_text

#Adds pc deals
pc_counter = 0
if len(pcDeals) > 0:
  for title, url in pcDeals.items():
    if pc_counter == 20:
      break
    pcdeal_text += link.format(url,title)
    addPCDeal = value_text.format(title,url)
    if(len(webhook_pcdeal_text) + len(addPCDeal) > 2000):
      wpdText.append(webhook_pcdeal_text)
      webhook_pcdeal_text = ">>> " + addPCDeal
    else:
      webhook_pcdeal_text += addPCDeal
    pc_counter += 1
  wpdText.append(webhook_pcdeal_text)
else:
  pcdeal_text += "Nothing here today!"
  webhook_pcdeal_text += "Nothing here today!"
  wpdText[0] = webhook_pcdeal_text

#Attaches deals to the email
html = html_body.format(deal_text, gamedeal_text, freeby_text, pcdeal_text)
message.attach(MIMEText(html, "html"))

#Sends email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
  server.login(env.EMAIL, env.EMAIL_PASSWORD)
  #server.sendmail(env.EMAIL, receiver_emails, message.as_string())

#Sets up webhooks
webhooks = []
for msg in wdText:
  webhooks.append(DiscordWebhook(url=env.WEBHOOKS_DEALS, content=msg))
for msg in wgdText:
  webhooks.append(DiscordWebhook(url=env.WEBHOOKS_GAMEDEALS, content=msg))
for msg in wfText:
  webhooks.append(DiscordWebhook(url=env.WEBHOOKS_FREEBIES, content=msg))
for msg in wpdText:
  webhooks.append(DiscordWebhook(url=env.WEBHOOKS_PCDEALS, content=msg))

#Executes webhooks
for wb in webhooks:
  wb.execute()