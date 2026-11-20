# SPDX-FileCopyrightText: 2026 Pardha Saradhi Edupalli
# SPDX-License-Identifier: MIT

"""Classify top-level YouTube comments and visualize counts by video."""
import argparse
import csv
import os
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

LABELS = ("positive", "neutral", "negative")
ROOT = Path(__file__).resolve().parent


def polarity_label(score):
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"


def collect_live_comments(api_key):
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    youtube = build("youtube", "v3", developerKey=api_key, cache_discovery=False)
    videos = youtube.videos().list(part="snippet", chart="mostPopular", regionCode="US",
                                   maxResults=10).execute()
    for video in videos.get("items", []):
        try:
            page = youtube.commentThreads().list(part="snippet", videoId=video["id"],
                                                  textFormat="plainText", maxResults=20).execute()
        except HttpError as exc:
            if exc.status_code == 403 and any(
                item.get("reason") == "commentsDisabled"
                for item in (exc.error_details if isinstance(exc.error_details, list) else [])
                if isinstance(item, dict)
            ):
                continue
            # Some client error strings include request URLs. Display only the status.
            raise SystemExit(f"YouTube comment request failed (HTTP {exc.status_code}).") from None
        for item in page.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            yield video["snippet"]["title"], snippet["textDisplay"]


def summarize(comments):
    from textblob import TextBlob

    counts = {}
    for title, comment in comments:
        counts.setdefault(title, Counter())[polarity_label(TextBlob(comment).sentiment.polarity)] += 1
    return counts


def plot(counts, destination):
    titles = list(counts)
    fig, ax = plt.subplots(figsize=(9, max(3, 0.55 * len(titles) + 2)), layout="constrained")
    base = [0] * len(titles)
    for label, color in zip(LABELS, ["#33825b", "#a8aebb", "#bc5c4b"]):
        values = [counts[title][label] for title in titles]
        ax.barh(range(len(titles)), values, left=base, label=label.title(), color=color)
        base = [previous + value for previous, value in zip(base, values)]
    ax.set_yticks(range(len(titles)), [t if len(t) <= 52 else t[:49] + "…" for t in titles])
    ax.set_xlabel("Sampled top-level comments")
    ax.set_title("Comment sentiment by video", loc="left")
    ax.legend()
    fig.savefig(destination, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Read comments using YOUTUBE_API_KEY")
    args = parser.parse_args()
    if args.live:
        from googleapiclient.errors import HttpError

        key = os.environ.get("YOUTUBE_API_KEY")
        if not key:
            raise SystemExit("Set YOUTUBE_API_KEY in your local environment first.")
        try:
            counts = summarize(collect_live_comments(key))
        except HttpError as exc:
            raise SystemExit(f"YouTube request failed (HTTP {exc.status_code}).") from None
    else:
        with (ROOT / "sample_comments.csv").open(encoding="utf-8", newline="") as file:
            counts = summarize((r["title"], r["comment"]) for r in csv.DictReader(file))
    if not counts:
        raise SystemExit("No top-level comments were available.")
    for title, tally in counts.items():
        print(title, {label: tally[label] for label in LABELS})
    plot(counts, Path("sentiment.png"))
    print("Saved sentiment.png")


if __name__ == "__main__":
    main()
