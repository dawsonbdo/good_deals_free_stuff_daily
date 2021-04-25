#!/usr/bin/env python3

import praw
import environment as env
from collections import defaultdict
from discord_webhook import DiscordWebhook, DiscordEmbed
import pickle

# Sets up Reddit praw API
reddit = praw.Reddit(client_id=env.CLIENT_ID, client_secret=env.CLIENT_SECRET, user_agent=env.USER_AGENT)

# Gets all previous titles from pickled dictionary
try:
    previous3070 = pickle.load(open("previous3070.save", "r+b"))
except:
    previous3070 = {}

try:
    previous3080 = pickle.load(open("previous3080.save", "r+b"))
except:
    previous3080 = {}

# Gets deals
deals3070 = defaultdict(list)
deals3080 = defaultdict(list)
for submission in reddit.subreddit("buildapcsales").new():
    if "[Prebuilt]" in submission.title and "3080" in submission.title:
        deals3080[submission.title] = "https://reddit.com" + submission.permalink
    elif "[Prebuilt]" in submission.title and "3070" in submission.title:
        deals3070[submission.title] = "https://reddit.com" + submission.permalink

# Checks if previously sent same message or not
deals3070Exist = True
deals3080Exist = True
newDeals3070 = defaultdict(list)
newDeals3080 = defaultdict(list)

# Checks for 3070s
if len(deals3070) > 0:
    for k,v in deals3070.items():
        if k not in previous3070:
            newDeals3070[k] = v
            previous3070[k] = v
else:
    deals3070 = False

# Checks for 3080s
if len(deals3080) > 0:
    for k,v in deals3080.items():
        if k not in previous3080:
            newDeals3080[k] = v
            previous3080[k] = v
else:
    deals3080 = False

if(len(newDeals3070) == 0):
    deals3070Exist = False
if(len(newDeals3080) == 0):
    deals3080Exist = False

# No new deals, quit
if deals3070Exist == False and deals3080Exist == False:
    quit()

# Saves newDeals with pickle
if deals3070Exist:
    pickle.dump(previous3070, open("previous3070.save", "a+b"))
if deals3080Exist:
    pickle.dump(previous3080, open("previous3080.save", "a+b"))

# Text for webhook
value_text = "- [{}](<{}>)\n"
webhook_deals3070_text = "***New 3070 Prebuilt Deal(s)!***\n>>> "
webhook_deals3080_text = "***New 3080 Prebuilt Deal(s)!***\n>>> "

# For times when there are a lot of posts (2000+ characters)
wd3070Text = []
wd3080Text = []

# Adds 3070 deals
if deals3070Exist:
    for title, url in newDeals3070.items():
        addDeal = value_text.format(title,url)
        if(len(webhook_deals3070_text) + len(addDeal) > 2000):
            wd3070Text.append(webhook_deals3070_text)
            webhook_deals3070_text = ">>> " + addDeal
        else:
            webhook_deals3070_text += addDeal
    wd3070Text.append(webhook_deals3070_text)

# Adds 3080 deals
if deals3080Exist:
    for title, url in newDeals3080.items():
        addDeal = value_text.format(title,url)
        if(len(webhook_deals3080_text) + len(addDeal) > 2000):
            wd3080Text.append(webhook_deals3080_text)
            webhook_deals3080_text = ">>> " + addDeal
        else:
            webhook_deals3080_text += addDeal
    wd3080Text.append(webhook_deals3080_text)

# Sets up webhooks
webhooks = []
if deals3070Exist:
    for msg in wd3070Text:
        webhooks.append(DiscordWebhook(url=env.WEBHOOKS_PREBUILTS, content=msg))
if deals3080Exist:
    for msg in wd3080Text:
        webhooks.append(DiscordWebhook(url=env.WEBHOOKS_PREBUILTS, content=msg))

# Executes webhooks
for wb in webhooks:
    wb.execute()
