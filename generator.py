import json
import anthropic
from tavily import TavilyClient

SEARCH_QUERIES = [
    "AI model releases developer tools this week 2026",
    "AI developer tooling pricing changes software engineers 2026",
    "AI impact software engineering jobs skills workforce 2026",
    "GitHub trending AI native developer tools agents CLI 2026",
    "software engineering culture industry shift AI 2026",
]

PROMPT = """You are curating a weekly newsletter for software developers. Based on the search results below, identify 6-8 of the most significant stories from the past 7 days.

Filter rules:
- INCLUDE: AI model/tool releases, developer tooling/pricing changes, job market/skills impact on engineers, engineering culture shifts, GitHub trending repos (AI-native dev tools, agent frameworks, coding agent CLIs, orchestration layers)
- EXCLUDE: pure funding rounds, pure benchmark hype, stories with no actionable developer angle
- For trending repos: skip flashy demos with no real adoption signal; only include repos solving a real dev workflow problem

Search results:
{context}

Respond with ONLY valid JSON, no markdown fences:
{{
  "week": "e.g. June 21-27, 2026",
  "stories": [
    {{
      "headline": "under 9 words, punchy",
      "what_happened": "2 plain-language sentences, no jargon",
      "why_care": "1-2 sentences focused on career or skill angle for a developer",
      "trend": "one sentence: ongoing shift or one-off event",
      "source_name": "publication or site name",
      "source_url": "https://..."
    }}
  ],
  "reel_picks": [
    {{
      "story_index": 0,
      "why": "1-2 sentences on why this works for a developer career-advice Instagram Reel"
    }},
    {{
      "story_index": 1,
      "why": "..."
    }}
  ]
}}"""


def generate_newsletter(anthropic_key: str, tavily_key: str) -> dict:
    tavily = TavilyClient(api_key=tavily_key)

    results = []
    for q in SEARCH_QUERIES:
        r = tavily.search(q, max_results=5, days=7)
        results.extend(r.get("results", []))

    seen, unique = set(), []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    context = "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r.get('content', '')[:600]}"
        for r in unique
    )

    client = anthropic.Anthropic(api_key=anthropic_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": PROMPT.format(context=context)}],
    )

    text = msg.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]

    return json.loads(text.strip())
