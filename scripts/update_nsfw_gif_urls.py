#!/bin/python3

import os
import sys
import json

# make sure we can import from src
sys.path.append(".")

from src import reddit

amount = 100
filename = "./data/p_urls.json"
print(f"[+] Updating NSFW gif URL list with {amount} URLs...")

posts = reddit.get_posts(subreddit="PornGifs", amount=amount)
urls = list()
error_count = 0
not_gif_count = 0
for post in posts:
    try:
        url = post["data"]["url"]
    except KeyError:
        error_count += 1
        continue
    else:
        if url.endswith(".gif") or url.endswith(".gifv"):
            urls.append(url)
        else:
            not_gif_count += 1

print(f"Queried {len(posts)} posts.")
print(f"Found {len(posts) - error_count} URLs.")
if error_count > 0:
    print(f"Failed to get {error_count} URLs.")
if not_gif_count > 0:
    print(f"URLs that were not a gif: {not_gif_count}")

os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    json.dump(urls, f)

print(f"Wrote {len(urls)} URLs to {filename}")
