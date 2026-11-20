import json
from collections import Counter
from pathlib import Path

import requests


BASE_URL = "https://jsonplaceholder.typicode.com"


def fetch_records(endpoint: str) -> list[dict]:
    """Fetch a list of records from one API endpoint."""
    url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(url, timeout=10)
        print(
            f"GET /{endpoint}  {response.status_code}  "
            f"{response.elapsed.total_seconds():.2f}s  "
            f"{response.headers.get('Content-Type', 'unknown')}"
        )
        response.raise_for_status()
        records = response.json()

        if not isinstance(records, list):
            raise ValueError(f"Expected a list from /{endpoint}")

        return records

    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request to /{endpoint} timed out") from None
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Could not connect to /{endpoint}") from None
    except requests.exceptions.HTTPError:
        raise RuntimeError(
            f"Request to /{endpoint} failed with HTTP {response.status_code}"
        ) from None
    except (requests.exceptions.JSONDecodeError, ValueError) as error:
        raise RuntimeError(f"Invalid API response from /{endpoint}: {error}") from None


def make_report(users: list[dict], posts: list[dict],
                comments: list[dict]) -> dict:
    """Count posts and comments using their matching IDs."""
    post_counts = Counter(post["userId"] for post in posts)
    post_owners = {post["id"]: post["userId"] for post in posts}
    comment_counts = Counter()

    for comment in comments:
        owner_id = post_owners.get(comment["postId"])
        if owner_id is not None:
            comment_counts[owner_id] += 1

    posts_per_user = {
        user["name"]: post_counts[user["id"]] for user in users
    }

    # The average uses the character count of each post's body.
    average_length = (
        sum(len(post["body"]) for post in posts) / len(posts)
        if posts else 0
    )

    top_user = None
    if users:
        leader = max(users, key=lambda user: comment_counts[user["id"]])
        top_user = {
            "name": leader["name"],
            "comment_count": comment_counts[leader["id"]]
        }

    return {
        "posts_per_user": posts_per_user,
        "top_user_by_comments": top_user,
        "average_post_length": round(average_length, 2)
    }


def main() -> None:
    try:
        users = fetch_records("users")
        posts = fetch_records("posts")
        comments = fetch_records("comments")
        report = make_report(users, posts, comments)

        with Path("report.json").open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2)

        top_user = report["top_user_by_comments"]
        if top_user:
            print(
                f"Top user by comments: {top_user['name']} "
                f"({top_user['comment_count']} comments)"
            )
        print("Report saved to report.json")

    except RuntimeError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
