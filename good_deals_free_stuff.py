#!/usr/bin/env python3

import smtplib, ssl
import praw
import os
from collections import defaultdict
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

link = "<li><a href=\"{}\">{}</a></li>"
deal_text = ""
gamedeal_text = ""
freeby_text = ""

#Adds deals
if len(deals) > 0:
  for title, url in deals.items():
    deal_text += link.format(url,title)
else:
  deal_text += "Nothing here today!"

#Adds game deals
if len(gameDeals) > 0:
  for title, url in gameDeals.items():
    gamedeal_text += link.format(url,title)
else:
  gamedeal_text += "Nothing here today!"

#Adds freebies
if len(freebies) > 0:
  for title, url in freebies.items():
    freeby_text += link.format(url,title)
else:
  freeby_text += "Nothing here today!"

#Attaches deals to the email
html = html_body.format(deal_text, gamedeal_text, freeby_text)
message.attach(MIMEText(html, "html"))

#Sends email
context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
  server.login(sender_email, sender_password)
  server.sendmail(sender_email, receiver_emails, message.as_string())
