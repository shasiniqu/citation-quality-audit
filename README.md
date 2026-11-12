# citation-quality-audit

An agent skill for auditing citation quality in a thesis or paper: build an argument map to decide which claims are load-bearing, grade each cited source (venue, journal track record, authors, impact, recency), and flag load-bearing claims backed only by weak sources.

- `SKILL.md` — the skill (Chinese)
- `templates/argument-map.md` — argument map template
- `scripts/openalex_lookup.py` — DOI/title → type, venue, citations, venue h-index, authors via the OpenAlex API (no key needed)
