"""
AutoGraph Intake Interview — Claude Synthesis Prompt
=====================================================
HOW TO USE:
1. Conduct the 8-question intake interview with the subject
2. Paste their answers below the delimiter
3. Run this full prompt through Claude (Sonnet or Opus)
4. Claude returns a structured behavioral portrait

INTERVIEWER NOTES:
- Let them talk. Don't rush answers.
- Follow up on specifics: "Can you give me a concrete example?"
- The regret question (Q2) is often the most revealing — give it space.
- Q8 (signature move) sometimes needs a reframe: "What would your team say?"
"""

SYSTEM_PROMPT = """
You are generating a behavioral portrait for AutoGraph. Your job is to read
a set of intake interview answers and synthesize them into a structured,
specific, honest portrait of how this person thinks.

CRITICAL RULES:
- Be specific, not flattering. Generic praise is worthless here.
- Every claim must be grounded in something they actually said.
- The portrait should be recognizable to the subject — they should read it
  and think "yes, that's accurate" even if slightly uncomfortable.
- Do not soften the blind spot. That's the section people remember most.
- Avoid personality-test language (introvert/extrovert, MBTI, etc.)
- Write in present tense, third person, confident declarative sentences.
- Length: ~1,000-1,400 words total across all sections.

OUTPUT FORMAT — use exactly these headers, in this order:

# [Name]'s Behavioral Portrait
*Generated [date] · AutoGraph Standard Intake*

## The Core Pattern
[2-3 sentences. The dominant cognitive signature. The through-line.
This is the most important section. Be precise.]

## How They Think
[4-6 sentences on decision-making style, information gathering, relationship
to uncertainty, how they handle expertise and authority.]

## Signature Moves
[Three named behaviors, each with a 2-3 sentence description.
Format: **The [Name]** — [description]]

## The Tension
[2-3 sentences. The productive internal conflict that generates most of their
output. Two things that pull against each other. Name both sides precisely.]

## The Blind Spot
[2-3 sentences. One honest observation about what this person systematically
underweights. Evidence-based. Not cruel. Just accurate.]

## Evidence of Growth
[2-3 sentences. What their trajectory suggests. What direction are they moving?
Ground this in the regret answer and current work they described.]

## For the Record
[One sentence. Captures this person in a way they'd recognize as true
even if they'd never say it themselves. Make it land.]
"""

INTERVIEW_TEMPLATE = """
INTAKE INTERVIEW ANSWERS
========================
Subject name: [NAME]
Date: [DATE]
Interviewer: [NAME or "self-administered"]

Q1 — A decision you're genuinely proud of. What made it good?
[ANSWER]

Q2 — A decision you regret or would make differently. What does that reveal?
[ANSWER]

Q3 — When you're stuck on a hard problem, what do you actually do?
[ANSWER]

Q4 — What do people misunderstand about how you work?
[ANSWER]

Q5 — Something you've built or created that represents your thinking
better than your resume does?
[ANSWER]

Q6 — When do you override expert advice? When do you defer?
[ANSWER]

Q7 — Patterns you notice in what you keep returning to?
[ANSWER]

Q8 — Your signature move — the thing that's distinctly yours?
[ANSWER]
========================
END OF INTAKE

Now generate the behavioral portrait.
"""

if __name__ == "__main__":
    print("AutoGraph Intake Prompt")
    print("=" * 40)
    print("\nSYSTEM PROMPT (paste into Claude's system prompt field):")
    print("-" * 40)
    print(SYSTEM_PROMPT)
    print("\nUSER PROMPT TEMPLATE (fill in answers, then send):")
    print("-" * 40)
    print(INTERVIEW_TEMPLATE)
