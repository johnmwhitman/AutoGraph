# AutoGraph Intake Processor — Claude API Edition
# v2.0: Updated for behavioral probe intake questions (2026-03-25)
#
# Expected intake JSON schema:
# {
#   "name": "Client Name",
#   "date": "2026-03-25",
#   "answers": {
#     "q1_proud_decision":      "...",  (v2: what you actually did in the moment)
#     "q2_regret_action":       "...",  (v2: what you did instead of what you knew)
#     "q3_built_created":       "...",  (v2: something that represents how you think)
#     "q4_group_disagreement":  "...",  (v2: room where people disagreed with you)
#     "q5_obsessive_problem":   "...",  (v2: what you can't leave alone)
#     "q6_uninvited_fix":       "...",  (v2: situation that wasn't yours but you fixed)
#     "q7_deferred_judgment":   "...",  (v2: time you deferred and it was right)
#     "q8_insider_knowledge":   "..."   (v2: what close collaborators know that others don't)
#   }
# }
#
# Usage:
#   python intake_processor.py <intake.json>   -- process intake file
#   python intake_processor.py --demo          -- use SAMPLE_INTAKE demo data

import json
import os
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Demo intake — v2 behavioral probe edition
# ---------------------------------------------------------------------------
SAMPLE_INTAKE = {
    "name": "Alex Rivera",
    "date": "2026-03-25",
    "answers": {
        "q1_proud_decision": (
            "I shut down a product line generating $400K/year. In the moment: I had run the "
            "model three times, kept getting the same answer, and stopped waiting for someone "
            "to tell me it was okay to act on it. I didn't announce the decision — I just "
            "moved to implementation and let the results make the case."
        ),
        "q2_regret_action": (
            "I kept a VP of Sales six months too long. What I did instead of what I knew: "
            "I scheduled a performance review, wrote detailed notes, then rescheduled it. "
            "Twice. I was building a case I already had. We lost two enterprise deals in "
            "that window. The file was complete on day 30. I waited until day 210."
        ),
        "q3_built_created": (
            "A competitive intelligence system I built on my own time that tracked 40 "
            "competitors across pricing, positioning, and hiring patterns. Nobody asked for "
            "it. It never shipped as a product. It reveals that I maintain a live map of a "
            "category by default — not to make a deck, but because I find surveillance of "
            "a whole system more interesting than any individual decision within it."
        ),
        "q4_group_disagreement": (
            "Board meeting, Q3 planning. Everyone in the room wanted to expand into a "
            "new vertical. I had the retention data showing we hadn't earned expansion in "
            "the core. I said it once, clearly, with the numbers. The room went quiet. "
            "Then the CFO agreed. We didn't expand. That quarter was our best retention ever. "
            "What I did: I didn't repeat myself or get louder. I said it once and let the "
            "data do the rest of the work."
        ),
        "q5_obsessive_problem": (
            "What makes something defensible — not just good. Why some companies can charge "
            "a premium and others with better products can't. I've been turning this over "
            "for eight years across three different industries. I still don't have a clean "
            "answer. I think the answer has something to do with who the customer is "
            "defending against when they choose you."
        ),
        "q6_uninvited_fix": (
            "Customer success team at a previous company was hemorrhaging renewals. Wasn't "
            "my org. I built a churn prediction model on a weekend using our own data, "
            "handed it to their director on Monday with a one-page brief. She used it. "
            "Renewals improved 23% that quarter. What triggered it: I couldn't watch a "
            "solvable problem go unsolved because of an org chart."
        ),
        "q7_deferred_judgment": (
            "Engineering lead pushed back hard on a three-month timeline I'd committed to "
            "externally. My instinct was to find a way to hold the date. What made me defer: "
            "she had built this system and I hadn't. Her objection was specific — a "
            "dependency I'd treated as resolved that wasn't. I called the client, reset "
            "the timeline. We shipped clean. If I'd held the date we'd have shipped broken."
        ),
        "q8_insider_knowledge": (
            "That I've usually already made the decision before the meeting starts. "
            "The meeting is me checking whether I missed something, not me forming a view. "
            "People who've worked with me closely know to bring the thing I might have "
            "missed — not to try to change my mind with the argument I've already run."
        )
    }
}


# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
def load_api_key() -> str:
    """
    Load ANTHROPIC_API_KEY with three-level fallback:
      1. Process environment (os.environ)
      2. Windows Machine-level registry
      3. C:\\AI\\.env file (utf-8-sig handles BOM)
    """
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key

    try:
        import winreg
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        )
        key, _ = winreg.QueryValueEx(reg_key, "ANTHROPIC_API_KEY")
        winreg.CloseKey(reg_key)
        if key and key.strip():
            return key.strip()
    except Exception:
        pass

    env_path = Path(r"C:\AI\.env")
    if not env_path.exists():
        print("ERROR: C:\\AI\\.env not found and no machine env key available.")
        sys.exit(1)
    with open(env_path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY=") and not line.startswith("ANTHROPIC_API_KEY_"):
                return line.split("=", 1)[1].strip()

    print("ERROR: ANTHROPIC_API_KEY not found")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Build user message
# ---------------------------------------------------------------------------
def build_user_message(intake: dict) -> str:
    """Fill INTERVIEW_TEMPLATE with intake answers. Slots filled by position Q1-Q8."""
    from intake_prompt import INTERVIEW_TEMPLATE

    answers = intake.get("answers", {})
    name    = intake.get("name", "Client")
    date    = intake.get("date", datetime.now().strftime("%Y-%m-%d"))

    q_keys = [
        "q1_proud_decision",
        "q2_regret_action",
        "q3_built_created",
        "q4_group_disagreement",
        "q5_obsessive_problem",
        "q6_uninvited_fix",
        "q7_deferred_judgment",
        "q8_insider_knowledge",
    ]

    filled = INTERVIEW_TEMPLATE
    filled = filled.replace("[NAME]", name, 2)
    filled = filled.replace("[DATE]", date, 1)

    for key in q_keys:
        answer = answers.get(key, "[No answer provided]")
        filled = filled.replace("[ANSWER]", answer, 1)

    return filled


# ---------------------------------------------------------------------------
# Core synthesis
# ---------------------------------------------------------------------------
def synthesize_portrait(intake: dict) -> str:
    """Send intake to Claude API, return portrait text."""
    import anthropic
    from intake_prompt import SYSTEM_PROMPT

    api_key = load_api_key()
    name    = intake.get("name", "Client")

    print(f"Synthesizing portrait for {name}...")

    client = anthropic.Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(intake)}]
        )
    except anthropic.APIError as e:
        print(f"ERROR: Anthropic API call failed — {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected failure — {e}")
        sys.exit(1)

    return message.content[0].text


# ---------------------------------------------------------------------------
# Write portrait to disk
# ---------------------------------------------------------------------------
def write_portrait(name: str, portrait_text: str) -> Path:
    portraits_dir = Path(__file__).parent / "portraits"
    portraits_dir.mkdir(exist_ok=True)
    name_slug = name.lower().replace(" ", "_")
    date_slug = datetime.now().strftime("%Y%m%d")
    out_path  = portraits_dir / f"{name_slug}_{date_slug}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(portrait_text)
    return out_path


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if "--demo" in sys.argv:
        intake = SAMPLE_INTAKE
        print("[DEMO MODE — behavioral probe v2 sample intake]\n")
    elif len(sys.argv) > 1:
        intake_path = sys.argv[1]
        if not os.path.exists(intake_path):
            print(f"ERROR: File not found — {intake_path}")
            sys.exit(1)
        with open(intake_path, encoding="utf-8") as f:
            intake = json.load(f)
    else:
        print("Usage: python intake_processor.py <intake.json>")
        print("       python intake_processor.py --demo")
        sys.exit(1)

    portrait_text = synthesize_portrait(intake)
    out_path      = write_portrait(intake.get("name", "client"), portrait_text)

    print(f"\nPortrait written to: {out_path}")
    print(f"\n{'='*60}")
    print(portrait_text[:200])
    print("...")
