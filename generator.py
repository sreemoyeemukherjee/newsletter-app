import json
import os
from datetime import datetime, timedelta

import anthropic
from tavily import TavilyClient

SEARCH_QUERIES = [
    "AI model releases developer tools past week",
    "software engineering AI tools pricing changes 2026",
    "AI impact software developer jobs skills 2026",
    "GitHub trending AI developer tools agent frameworks",
    "engineering culture AI-first developer workflow 2026",
]

SYSTEM_PROMPT = """You are a sharp, opinionated tech editor writing a weekly newsletter for working software developers and aspiring engineers. Your job is to curate what actually matters — not hype, not VC theatre, not benchmark wars with no real-world meaning.

You will be given raw search results from the past 7 days. Your task is to produce structured JSON output only — no markdown prose outside the JSON, no preamble, no explanation.

The JSON must follow this exact schema:
{
  "stories": [
    {
      "headline": "short punchy headline under 9 words",
      "what_happened": "2 plain-language sentences, no jargon",
      "why_dev_should_care": "1-2 sentences, career/skill angle specifically",
      "trend_or_oneoff": "one sentence — is this part of an ongoing shift or isolated?",
      "source_name": "Publication or site name",
      "source_url": "URL"
    }
  ],
  "top_picks": {
    "pick_1": {
      "story_headline": "headline of the chosen story",
      "reel_angle": "why this is great for a career advice Instagram Reel — 2-3 sentences"
    },
    "pick_2": {
      "story_headline": "headline of the chosen story",
      "reel_angle": "why this is great for a career advice Instagram Reel — 2-3 sentences"
    },
    "why_these_two": "1-2 sentences explaining why these over the others"
  }
}

Filtering rules you must apply:
- Include 6-8 stories total
- At least one must be a GitHub trending repo (if a strong one exists) — only include repos solving a real workflow problem with adoption signal, not flashy demos
- Skip pure funding rounds with no developer-actionable angle
- Skip pure benchmark comparisons with no tool/workflow impact
- Skip stories with no actionable insight for an individual developer's career or workflow
- The top 2 picks must have a strong "career advice for developers" Instagram Reel angle"""

USER_PROMPT_TEMPLATE = """Today is {today}. Here are web search results from the past 7 days:

{search_results}

Apply your filtering rules strictly. Return only the JSON object — nothing else."""


def run_searches(tavily_client: TavilyClient) -> str:
    all_results = []
    for query in SEARCH_QUERIES:
        try:
            response = tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                days=7,
            )
            for r in response.get("results", []):
                all_results.append(
                    f"SOURCE: {r.get('url', '')}\nTITLE: {r.get('title', '')}\nSNIPPET: {r.get('content', '')[:400]}\n"
                )
        except Exception as e:
            print(f"Search failed for '{query}': {e}")

    return "\n---\n".join(all_results)


def generate_newsletter() -> dict:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not anthropic_key or not tavily_key:
        raise ValueError("ANTHROPIC_API_KEY and TAVILY_API_KEY must be set in .env")

    tavily = TavilyClient(api_key=tavily_key)
    claude = anthropic.Anthropic(api_key=anthropic_key)

    print("Running Tavily searches...")
    search_results = run_searches(tavily)

    today = datetime.now().strftime("%B %d, %Y")
    user_prompt = USER_PROMPT_TEMPLATE.format(today=today, search_results=search_results)

    print("Calling Claude...")
    message = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if Claude wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)
    return parsed, raw


def week_label() -> str:
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return f"Week of {monday.strftime('%b %d')} – {friday.strftime('%b %d, %Y')}"
