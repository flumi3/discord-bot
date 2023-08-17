#!/bin/python3

import os
import json
import requests

amount = 6000
filename = "./data/p_urls.json"
print(f"[+] Updating NSFW gif URL list with {amount} URLs...")


def get_reddit_posts(subreddit: str, sort: str = "top", timeframe: str = "all", amount: int = 100) -> list:
    """Queries a list of posts from a subreddit.

    Args:
        subreddit (str): The subreddit to query.
        sort (str, optional): The sorting method to use. Defaults to "top".
        timeframe (str, optional): The timeframe to query. Defaults to "all".
        limit (int, optional): The number of posts to query. Defaults to 10.

    Returns:
        list: A list of posts.
    """
    print(f"Querying Reddit API for {amount} {sort} posts from r/{subreddit}...")
    posts = []
    after = ""
    initial_amount = amount
    while len(posts) < initial_amount and amount > 0:
        if amount > 100:
            limit = 100
        else:
            limit = amount

        if not after:
            url = f"https://reddit.com/r/{subreddit}/{sort}.json?limit={limit}&t={timeframe}&raw_json=1"
        else:
            url = f"https://reddit.com/r/{subreddit}/{sort}.json?limit={limit}&t={timeframe}&raw_json=1&after={after}"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}  # pretend to be a browser
        response = requests.get(url, headers=headers)
        r_content = response.json()
        posts.extend(r_content["data"]["children"])
        after = r_content["data"]["after"]  # used to get the next page of posts
        amount = amount - limit
    print(f"Retrieved {len(posts)} posts.")
    return posts


posts = get_reddit_posts(subreddit="PornGifs", amount=amount)
urls = list()
error_count = 0
imgur_link_count = 0
allowed_extensions = [
    ".gif",
    ".gifv",
    ".mp4",
    ".webm",
]
for post in posts:
    try:
        url = post["data"]["url"]
    except KeyError:
        error_count += 1
        continue
    else:
        if "imgur" in url:
            imgur_link_count += 1
        elif url.endswith(tuple(allowed_extensions)):
            urls.append(url)

print(f"Found {len(posts) - error_count} URLs.")
if error_count > 0:
    print(f"Failed to get {error_count} URLs.")
if imgur_link_count > 0:
    print(f"Sorted out {imgur_link_count} imgur links.")

os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    json.dump(urls, f)

print(f"Wrote {len(urls)} URLs to {filename}")
