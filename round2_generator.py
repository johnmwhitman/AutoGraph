# Thumbprint Round 2 Question Generator
# Reads a completed portrait .md and generates 8 personalized follow-up questions
# via the Claude API, grounded in what Round 1 actually found.
#
# Usage:
#   python round2_generator.py <portrait_file.md>
#   python round2_generator.py --demo   (uses most recent portrait in portraits/)

import os
import sys
from datetime import datetime
from pathlib import Path


BASE_DIR         = Path(__file__).parent
PORTRAITS_DIR    = BASE_DIR / "portraits"
ROUND2_QUESTIONS = BASE_DIR / "round2_questions"

SYSTEM_PROMPT = """You are generating Round 2 intake questions for Thumbprint.

Round 1 produced a behavioral portrait. You have read it.
Your job: write 8 follow-up questions that probe DEEPER into what Round 1 found.

Rules:
- Every question must reference a specific pattern, tension, or blind spot
  identified in the portrait — not a generic question about them
- Questions should surface evidence that would CONFIRM or COMPLICATE the
  Round 1 findings — not just validate them
- At least 2 questions should probe the blind spot section directly
- At least 1 question should probe the tension section
- At least 1 question should be about a specific named behavior from
  Signature Moves, asked from an unexpected angle
- Questions must still be behavioral probes (specific incidents, not self-report)
- Format each question as a standalone question, numbered 1-8
- No preamble, no explanation — just the 8 questions

Example of a bad Round 2 question (generic):
"Tell me about another decision you're proud of."

Example of a good Round 2 question (portrait-specific):
[If portrait found: blind spot = interpersonal avoidance]
"Describe the last time you had a hard conversation you'd been delaying.
What finally made you have it? What did you do in the first 30 seconds?"

The portrait is in the user message. Generate 8 questions."""


# ---------------------------------------------------------------------------
# API key loader — three-level fallback
# ---------------------------------------------------------------------------
def load_api_key() -> str:
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
    if env_path.exists():
        with open(env_path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY=") and not line.startswith("ANTHROPIC_API_KEY_"):
                    return line.split("=", 1)[1].strip()
    print("ERROR: ANTHROPIC_API_KEY not found in env, registry, or C:\\AI\\.env")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Generate Round 2 questions from portrait
# ---------------------------------------------------------------------------
def generate_round2_questions(portrait_text: str) -> str:
    """Call Claude API with portrait, return 8 personalized questions."""
    import anthropic
    api_key = load_api_key()
    client  = anthropic.Anthropic(api_key=api_key)
    print("Generating Round 2 questions via Claude API...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": portrait_text}]
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Write questions to disk
# ---------------------------------------------------------------------------
def write_questions(name_slug: str, questions: str) -> Path:
    ROUND2_QUESTIONS.mkdir(exist_ok=True)
    date_slug = datetime.now().strftime("%Y%m%d")
    out_path  = ROUND2_QUESTIONS / f"{name_slug}_{date_slug}.md"
    header    = f"# Thumbprint Round 2 Questions\n# Client: {name_slug.replace('_', ' ').title()}\n# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + questions)
    return out_path


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if "--demo" in sys.argv or len(sys.argv) < 2:
        # Find most recent portrait
        portraits = sorted(PORTRAITS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not portraits:
            print("ERROR: No portraits found in", PORTRAITS_DIR)
            sys.exit(1)
        portrait_path = portraits[0]
        print(f"[DEMO] Using most recent portrait: {portrait_path.name}")
    else:
        portrait_path = Path(sys.argv[1])
        if not portrait_path.exists():
            print(f"ERROR: File not found — {portrait_path}")
            sys.exit(1)

    portrait_text = portrait_path.read_text(encoding="utf-8")
    # Derive name slug from filename (e.g. alex_rivera_20260325.md -> alex_rivera)
    stem_parts = portrait_path.stem.rsplit("_", 1)
    name_slug  = stem_parts[0] if len(stem_parts) > 1 and stem_parts[1].isdigit() else portrait_path.stem

    questions = generate_round2_questions(portrait_text)
    out_path  = write_questions(name_slug, questions)

    print(f"\nRound 2 questions written to: {out_path}")
    print(f"\n{'=' * 60}")
    print(questions)
