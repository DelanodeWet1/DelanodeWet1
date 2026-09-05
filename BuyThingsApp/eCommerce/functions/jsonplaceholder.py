import requests


def get_posts(user_id=None):
    """
    Retrieve sample posts from the JSONPlaceholder /posts endpoint.

    Args:
        user_id (int, optional): Filter posts by a specific sample user ID.

    Returns:
        list: A list of simplified post dictionaries. Returns an empty list
        if the request fails.
    """
    url = "https://jsonplaceholder.typicode.com/posts"
    params = {}

    # Add the userId query parameter only when a user ID is provided.
    if user_id is not None:
        params["userId"] = user_id

    try:
        # Send a GET request to the external REST API.
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        # Raise an exception if the API returns an unsuccessful status code.
        response.raise_for_status()

        # Convert the JSON response into Python data.
        data = response.json()
        posts = []

        # Extract only the fields needed by the Django application.
        for item in data:
            posts.append({
                "id": item["id"],
                "title": item["title"],
                "body": item["body"],
                "user_id": item["userId"]
            })

        return posts

    except requests.RequestException as error:
        # Print the error for development purposes and return an empty list
        # so that the Django page can display a fallback message.
        print(f"Unable to retrieve posts: {error}")
        return []