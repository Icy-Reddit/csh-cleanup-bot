#!/usr/bin/env python3
"""
GitHub Actions version of Yoori auto-approve.

Purpose:
- subreddit: r/CShortHaven ONLY
- user: u/Yoori_Lee ONLY
- approves Yoori's content if Reddit places it in Removed/Spam or Mod Queue
- skips items with reports
- skips items explicitly removed by a moderator

Credentials are read ONLY from environment variables supplied by GitHub Actions Secrets.
"""

import os
import sys
import time
import praw

SUBREDDIT = "CShortHaven"
TARGET_USER = "Yoori_Lee"
LISTING_LIMIT = 250
APPROVAL_DELAY = 0.35


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def author_name(item):
    try:
        return item.author.name if item.author else None
    except Exception:
        return None


def is_target(item):
    name = author_name(item)
    return bool(name and name.casefold() == TARGET_USER.casefold())


def has_reports(item):
    return bool(
        getattr(item, "user_reports", None)
        or getattr(item, "mod_reports", None)
    )


def removed_by_moderator(item):
    category = getattr(item, "removed_by_category", None)
    return str(category).casefold() == "moderator"


def item_kind(item):
    return "post" if item.__class__.__name__ == "Submission" else "comment"


def item_url(item):
    permalink = getattr(item, "permalink", None)
    return f"https://www.reddit.com{permalink}" if permalink else ""


def main():
    reddit = praw.Reddit(
        client_id=require_env("REDDIT_CLIENT_ID"),
        client_secret=require_env("REDDIT_CLIENT_SECRET"),
        username=require_env("REDDIT_USERNAME"),
        password=require_env("REDDIT_PASSWORD"),
        user_agent=os.getenv(
            "REDDIT_USER_AGENT",
            "CShortHaven Yoori AutoApprove/1.0 by Cleanup_Bot",
        ),
    )

    if reddit.read_only:
        raise RuntimeError("Reddit session is read-only.")

    me = reddit.user.me()
    print(f"Logged in as: u/{me}")
    print(f"Subreddit: r/{SUBREDDIT}")
    print(f"Target: u/{TARGET_USER}")

    subreddit = reddit.subreddit(SUBREDDIT)

    # De-duplicate items that may appear in both listings.
    seen = set()
    candidates = []

    sources = [
        ("removed", subreddit.mod.spam(limit=LISTING_LIMIT)),
        ("modqueue", subreddit.mod.modqueue(limit=LISTING_LIMIT)),
    ]

    for source_name, listing in sources:
        for item in listing:
            fullname = getattr(item, "fullname", None) or getattr(item, "id", None)
            if not fullname or fullname in seen:
                continue
            seen.add(fullname)

            if not is_target(item):
                continue

            if has_reports(item):
                print(f"SKIP reported {item_kind(item)}: {item_url(item)}")
                continue

            if removed_by_moderator(item):
                print(f"SKIP moderator-removed {item_kind(item)}: {item_url(item)}")
                continue

            candidates.append((source_name, item))

    print(f"Eligible items found: {len(candidates)}")

    approved = 0
    failed = 0

    for source_name, item in candidates:
        try:
            item.mod.approve()
            approved += 1
            print(
                f"APPROVED {item_kind(item)} [{source_name}] "
                f"{getattr(item, 'fullname', '')} {item_url(item)}"
            )
            time.sleep(APPROVAL_DELAY)
        except Exception as exc:
            failed += 1
            print(
                f"FAILED {item_kind(item)} "
                f"{getattr(item, 'fullname', '')}: "
                f"{type(exc).__name__}: {exc}"
            )

    print(f"Done. Approved={approved}, Failed={failed}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
