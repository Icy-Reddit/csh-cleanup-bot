# Yoori Auto-Approve — GitHub Actions

This repository runs a small GitHub Actions job every 5 minutes.

It is hard-coded to:
- subreddit: `r/CShortHaven`
- target: `u/Yoori_Lee`
- bot account: whatever account is stored in `REDDIT_USERNAME`

The script checks Reddit's Removed/Spam listing and Mod Queue.
It approves only Yoori's items and skips:
- reported items
- items explicitly removed by a moderator

## 1. Add these files to the repository

Keep this structure:

```text
.
├── .github/
│   └── workflows/
│       └── yoori-autoapprove.yml
├── yoori_autoapprove_github.py
└── requirements.txt
```

## 2. Add GitHub Actions Secrets

Repository → Settings → Secrets and variables → Actions → New repository secret

Create exactly these four secrets:

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`

Use the existing Cleanup Bot Reddit API credentials.

Do NOT put these values in the Python file, YAML file, README, commits, issues, or chat messages.

## 3. Make sure Cleanup Bot is a moderator

On `r/CShortHaven`, Cleanup Bot needs permission to manage posts/comments.

## 4. Test manually

Repository → Actions → `Yoori Auto-Approve` → Run workflow

Open the run log. It should show:

```text
Logged in as: u/...
Subreddit: r/CShortHaven
Target: u/Yoori_Lee
Eligible items found: ...
Done. Approved=..., Failed=...
```

## 5. Automatic operation

The workflow is scheduled every 5 minutes. GitHub scheduled jobs can occasionally start later than the exact cron time, so this is not an instant-response system.

To stop it, disable the workflow in the Actions tab or remove the `schedule:` block.
