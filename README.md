# Get daily messages with the best deals and free stuff
Uses Reddit's praw API to look over subreddits that contains deals and/or free stuff to redeem and sends an email daily reporting all this information for easy access.
Sends an email at 7PM PST everyday with links to the top daily posts from r/deals, r/GameDeals, r/eFreebies, r/buildapcsales.
Now also added Discord webhook functionality to send an automated message at the same time.

Python script is executed daily via cron on a Raspberry Pi 4.

Additional functionality implemented 4/25/21 to allow for alerts for prebuilt PCs with a 3070/3080 in them. 
