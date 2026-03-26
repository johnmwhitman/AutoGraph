"""
Thumbprint Intake Interview — Claude Synthesis Prompt
=====================================================
Version: 2.0 — Behavioral Probe Edition (revised 2026-03-25)

DESIGN PHILOSOPHY:
The original questions mixed behavioral probes with self-report. Self-report
gives you labels ("I'm decisive"). Behavioral probes give you demonstrations
("I shut down a $400K line because the model kept returning the same answer").
Synthesis runs on demonstrations, not labels.

Every question in v2 is designed to extract a specific incident or observable
behavior. The subject has to SHOW the pattern, not name it. What they choose
to show is itself data about who they are and what they value.

HOW TO USE:
1. Share the 8 questions with the subject (form, email, doc — any format)
2. Collect their written answers (encourage 2-5 sentences per question)
3. Run intake_processor.py with the answers as intake.json
4. Claude synthesizes the behavioral portrait

FORM DESIGN NOTE:
Questions should be presented without framing that signals what "correct"
looks like. No instructions like "be honest" or "think deeply." Just the
question. The answer given unprompted is the most informative version.

INTERVIEWER NOTES (for live sessions):
- The follow-up that unlocks everything: "What did you actually do?"
- Q2 (regret) is the most revealing — give it room, don't rush past it.
- Q4 (group disagreement) surfaces the interpersonal pattern most clearly.
- If an answer is abstract, ask: "Can you give me the specific situation?"
"""

SYSTEM_PROMPT = """
You are generating a behavioral portrait for Thumbprint. Your job is to read
a set of intake interview answers and synthesize them into a structured,
specific, honest portrait of how this person thinks and operates.

SYNTHESIS PRINCIPLES:
- Be specific, not flattering. Generic praise is worthless here.
- Every claim must trace back to something they actually demonstrated in their
  answers — not something they said about themselves. There is a difference.
  "I'm decisive" is self-report. "I ran the model three times and still shut
  down the product line" is demonstration. Synthesize from demonstrations.
- The portrait should be recognizable. They should read it and think "yes,
  that's accurate" — even if no one has said it to them quite this directly.
- Do not soften the blind spot. That section is often what they remember most.
  Being honest there is the product. Softening it breaks the product.
- Watch for the gap between what they say they value and what their stories
  actually show. That gap is often the most important thing in the portrait.
- Avoid personality-test language (introvert/extrovert, MBTI types, etc.)
- Write in present tense, third person, confident declarative sentences.
- Length: ~1,000-1,400 words total across all sections.

READING THE ANSWERS:
The question they chose to answer says as much as the content of the answer.
What incident they reached for when asked about pride — that's their definition
of success. How they describe a failure — that's their attribution style.
Whether they mention other people — that's their relational orientation.
What they built that "represents their thinking" — that's their actual values,
not their stated ones. Read the choices, not just the words.
"""
OUTPUT FORMAT — use exactly these headers, in this order:

# [Name]'s Behavioral Portrait
*Generated [date] · Thumbprint Standard Intake*

## The Core Pattern
[2-3 sentences. The dominant cognitive signature. The through-line that
connects all the different stories they told. Name it precisely — a label
they've probably never heard but will immediately recognize as accurate.]

## How They Think
[4-6 sentences on decision-making style, information processing, relationship
to uncertainty, how they handle expertise and authority. Ground every
sentence in specific evidence from their answers.]

## Signature Moves
[Three named behaviors, each with a 2-3 sentence description. Name them
specifically — not "analytical thinking" but "The Pre-Committed Model."
The name should capture what's distinctive about HOW they do the thing.
Format: **The [Name]** — [description]]

## The Tension
[2-3 sentences. The productive internal conflict that generates most of their
output. Two things that pull against each other. Name both sides precisely.
This is the engine. But it has a cost.]

## The Blind Spot
[2-3 sentences. One honest observation about what this person systematically
underweights or avoids. Evidence-based — trace it to something they said.
Not cruel. Just accurate. This is the section that earns trust if you get
it right, and breaks it if you make it generic.]

## Evidence of Growth
[2-3 sentences. What their trajectory suggests. What direction are they
actually moving? Ground this in the regret answer and whatever current work
or change they described. Avoid uplift. Report what the evidence shows.]

## For the Record
[One sentence. Captures this person in a way they'd recognize as true even
if they'd never say it themselves. The best version of this feels like
something a very perceptive friend might say after knowing them for years.
Make it land.]
"""

INTERVIEW_TEMPLATE = """
INTAKE INTERVIEW ANSWERS
========================
Subject name: [NAME]
Date: [DATE]
Interviewer: [NAME or "self-administered"]

Q1 — Describe a decision you made that you're genuinely proud of.
Walk me through what you actually did — not why it was right in hindsight,
but what you did in the moment when it was still uncertain.
[ANSWER]

Q2 — Describe a decision you'd make differently. Don't explain why it was
the wrong call — tell me what you did instead of what you knew you should do.
[ANSWER]

Q3 — Tell me about something you built or created that represents how you
think more honestly than your resume does. What is it, and what does it
reveal about you?
[ANSWER]

Q4 — Describe a situation where you were in a room with people who disagreed
with your read on something. What did you do? What happened?
[ANSWER]

Q5 — What problem do you keep coming back to — not because it's assigned to
you, but because you can't leave it alone?
[ANSWER]

Q6 — Tell me about a time you walked into a situation that wasn't yours to
fix and fixed it anyway. What triggered that?
[ANSWER]

Q7 — Describe a time you deferred to someone else's judgment and it was the
right call. What made you defer?
[ANSWER]

Q8 — What do the people who work most closely with you know about how you
operate that people who've just met you don't?
[ANSWER]
========================
END OF INTAKE

Now generate the behavioral portrait.
"""


if __name__ == "__main__":
    print("Thumbprint Intake Prompt v2.0 — Behavioral Probe Edition")
    print("=" * 55)
    print("\nSYSTEM PROMPT:")
    print("-" * 40)
    print(SYSTEM_PROMPT)
    print("\nINTERVIEW TEMPLATE:")
    print("-" * 40)
    print(INTERVIEW_TEMPLATE)
