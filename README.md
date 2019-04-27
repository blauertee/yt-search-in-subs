# Search in all of your youtube subscriptions

## Usage
`yt-search-in-subs.py <query> <subscription file>`

you can get the file with all your subscriptions in it from
https://www.youtube.com/subscription_manager?action_takeout=1

## Comments
Since the script performs an actual search on every of your subscribed channels and fetches the html it's dead slow (A query on a relatively modern Computer with a good internet connection (200k) takes around 0.5 seconds per subscription).
The Advantage of this is, that it actually uses the youtube search algorithm wich also searches in auto generated subtitles, tags etc.
