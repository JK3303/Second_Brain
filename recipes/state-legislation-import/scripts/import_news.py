"""
import_news.py
-------------
Fetches news articles about state legislation from NewsAPI and links
them to bills in sl_legislation via sl_news_sources.

NewsAPI docs: https://newsapi.org/docs
Free API key: https://newsapi.org/register (100 requests/day free tier)

For each topic, this script searches for recent news articles and
attempts to link them to existing bills by matching state name and
bill keywords.

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    NEWS_API_KEY=your-key \
    python import_news.py

Requirements:
    pip install supabase python-dotenv requests
"""

import os
import sys
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL         = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
NEWS_API_KEY         = os.environ.get("NEWS_API_KEY")

for var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "NEWS_API_KEY"):
    if not os.environ.get(var):
        sys.exit(f"ERROR: Set {var} environment variable.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

NEWSAPI_BASE  = "https://newsapi.org/v2/everything"
LOOKBACK_DAYS = 90  # How far back to search for articles

# Search queries per topic — focused on state-level legislative impact
TOPIC_QUERIES = {
    "healthcare":       "state healthcare reform legislation law passed",
    "housing":          "state housing legislation affordable housing law passed",
    "jobs":             "state job growth legislation minimum wage workforce law",
    "education":        "state education legislation school funding law passed",
    "criminal-justice": "state criminal justice reform legislation law passed",
    "environment":      "state climate energy legislation law passed",
    "taxes":            "state tax reform legislation law passed",
    "infrastructure":   "state infrastructure broadband legislation law passed",
    "immigration":      "state immigration legislation law passed",
    "voting":           "state voting election legislation law passed",
}

POSITIVE_WORDS = {"success", "improve", "benefit", "help", "boost", "positive",
                  "increase", "growth", "reduce", "lower", "save", "expand", "progress"}
NEGATIVE_WORDS = {"fail", "harm", "hurt", "worsen", "problem", "cost", "burden",
                  "crisis", "concern", "oppose", "backlash", "controversy", "cut"}


def infer_sentiment(text: str) -> str:
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    if pos > neg + 1:
        return "positive"
    elif neg > pos + 1:
        return "negative"
    elif pos > 0 and neg > 0:
        return "mixed"
    return "neutral"


def get_topic_id(slug: str) -> str | None:
    result = supabase.table("sl_topics").select("id").eq("slug", slug).limit(1).execute()
    return result.data[0]["id"] if result.data else None


def find_matching_legislation(headline: str, description: str) -> list[str]:
    """
    Attempts to match a news article to existing legislation by
    searching bill titles for keyword overlap.
    """
    text = f"{headline} {description}".lower()
    words = [w for w in text.split() if len(w) > 5][:10]
    if not words:
        return []

    matched_ids = []
    for word in words:
        result = (
            supabase.table("sl_legislation")
            .select("id")
            .ilike("title", f"%{word}%")
            .limit(3)
            .execute()
        )
        for row in result.data:
            if row["id"] not in matched_ids:
                matched_ids.append(row["id"])
    return matched_ids[:3]  # Cap at 3 matches per article


def fetch_articles(query: str) -> list[dict]:
    from_date = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    try:
        r = requests.get(
            NEWSAPI_BASE,
            params={
                "q":        query,
                "from":     from_date,
                "sortBy":   "relevancy",
                "language": "en",
                "pageSize": 20,
                "apiKey":   NEWS_API_KEY,
            },
            timeout=15,
        )
        r.raise_for_status()
        return r.json().get("articles", [])
    except requests.RequestException as e:
        print(f"    WARNING: NewsAPI failed — {e}")
        return []


def main() -> None:
    print("Importing news articles about state legislation...")
    total = 0

    for topic_slug, query in TOPIC_QUERIES.items():
        print(f"  → {topic_slug}")
        articles = fetch_articles(query)

        for article in articles:
            headline    = (article.get("title") or "").strip()
            description = (article.get("description") or "").strip()
            url         = article.get("url", "")
            outlet      = article.get("source", {}).get("name")
            pub_date    = (article.get("publishedAt") or "")[:10] or None

            if not headline or not url:
                continue

            sentiment = infer_sentiment(f"{headline} {description}")

            # Try to link to existing legislation
            legislation_ids = find_matching_legislation(headline, description)
            target_ids = legislation_ids if legislation_ids else [None]

            for leg_id in target_ids:
                # Check for duplicate
                existing = (
                    supabase.table("sl_news_sources")
                    .select("id")
                    .eq("url", url)
                    .limit(1)
                    .execute()
                )
                if existing.data:
                    continue

                if leg_id:
                    supabase.table("sl_news_sources").insert({
                        "legislation_id": leg_id,
                        "headline":       headline,
                        "outlet":         outlet,
                        "url":            url,
                        "published_date": pub_date,
                        "sentiment":      sentiment,
                        "excerpt":        description[:500] if description else None,
                    }).execute()
                    total += 1

        print(f"    Saved articles for {topic_slug}.")
        time.sleep(1)  # Respect rate limits

    print(f"\nDone. Imported {total} linked news articles.")


if __name__ == "__main__":
    main()
