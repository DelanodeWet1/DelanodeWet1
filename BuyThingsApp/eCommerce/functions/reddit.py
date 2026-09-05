import requests


def get_reddit_posts(subreddit="Python"):
    url = f"https://www.reddit.com/r/{subreddit}/.json"
    headers = {"User-Agent": "web:BuyThings:1.0 (by /u/Just_Dirt3486)"}

    # Reddit requires a User-Agent
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to fetch data: {response.status_code}"}
    data = response.json()
    posts = []
    for item in data["data"]["children"]:
        post = item["data"]
        posts.append(
            {"title": post["title"], "author": post["author"], "url": post["url"]}
        )
    return posts
