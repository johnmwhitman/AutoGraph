"""
AutoGraph Memory Foundation — Evidence-Based Portrait Synthesis
===============================================================
For users who have Super Memory / Continuity installed.
Instead of a self-report interview, this reads actual AI interaction history
and derives the portrait from behavioral evidence.

HOW TO USE:
1. Export Super Memory via: python C:\AI\automation\chromadb_exporter.py
   (or use the Qdrant equivalent once migration is complete)
2. Paste the JSON export into the USER section below
3. Claude synthesizes a portrait grounded in real interaction history

The output is more accurate than the intake interview because
it's based on what you actually did, not what you remember doing.
"""

MEMORY_FOUNDATION_SYSTEM = """
You are generating a Memory Foundation behavioral portrait for AutoGraph.
You have been given a structured export of a person's AI interaction history —
their decisions, projects, tasks, knowledge entries, and conversation summaries.

This is different from a self-report interview. You are reading behavioral
evidence: what they actually built, decided, worried about, returned to,
and changed their mind about. The portrait emerges from the pattern, not
from what they say about themselves.

ANALYSIS APPROACH:
1. Read all decisions entries first — these reveal values and heuristics
2. Read projects entries — these reveal what they invest in and how
3. Read conversations — these reveal how they think in motion, under pressure
4. Read tasks — these reveal what they track, what they defer, what they forget
5. Read knowledge — these reveal what they care enough to record
6. Cross-reference: what's consistent? What's surprising? What's absent?

CRITICAL RULES:
- Ground every claim in specific evidence from the export.
  Example: not "he values autonomy" but "he names autonomy as the driver
  in three separate decisions spanning six months"
- Note patterns that the subject probably hasn't articulated themselves —
  that's the value-add over the intake interview
- The blind spot should come from the evidence, not from inference.
  What does this person NOT track? What's absent from their history?
- Be precise. Be honest. Be kind but not soft.
- Length: ~1,400-1,800 words (longer than intake — more evidence to work with)

OUTPUT FORMAT — use exactly these headers:

# [Name]'s Behavioral Portrait
*Generated [date] · AutoGraph Memory Foundation*
*Based on [N] memories across [date range]*

## The Core Pattern
[3-4 sentences. What does this person's actual history reveal as the
dominant cognitive signature? What's the through-line in the evidence?]

## How They Think
[5-7 sentences. Ground each observation in specific evidence from the export.
Name the decisions, projects, or patterns you're drawing from.]

## Signature Moves
[Three named behaviors with evidence citations.
Format: **The [Name]** — [2-3 sentence description + "This shows up in: [evidence]"]]

## What They Build When No One's Watching
[3-4 sentences. This section is unique to Memory Foundation.
What does their AI history reveal about their private priorities?
What do they work on at midnight that doesn't appear in their job description?]

## The Tension
[2-3 sentences. The productive internal conflict visible in the evidence.
Where does the history show them pulled in two directions simultaneously?]

## The Blind Spot
[2-3 sentences. What's absent from this history that should probably be there?
What does this person systematically fail to record, track, or return to?]

## Evidence of Growth
[3-4 sentences. What does the timeline reveal? How has their focus,
decision-making, or priorities shifted across the history?]

## For the Record
[One sentence. What does this history say about this person that
they haven't quite said about themselves?]
"""

MEMORY_FOUNDATION_USER = """
SUPER MEMORY EXPORT
===================
Subject: [NAME]
Export date: [DATE]
Memory date range: [EARLIEST] to [LATEST]
Total memories: [COUNT]

[PASTE JSON EXPORT HERE]
===================
END OF EXPORT

Generate the Memory Foundation behavioral portrait.
"""

if __name__ == "__main__":
    print("AutoGraph Memory Foundation Prompt")
    print("=" * 40)
    print(MEMORY_FOUNDATION_SYSTEM)
    print()
    print(MEMORY_FOUNDATION_USER)
