# Thumbprint Coordinator — Portrait Lifecycle Tracker
# Tracks per-client state across all rounds and tiers.
#
# Commands:
#   python autograph_coordinator.py --list
#   python autograph_coordinator.py --status <name_slug>
#   python autograph_coordinator.py --next-action <name_slug>
#   python autograph_coordinator.py --generate-round2 <name_slug>
#   python autograph_coordinator.py --new <name> <email> <tier>
#
# Portrait states (in order):
#   round1_intake_received → round1_synthesizing → round1_delivered
#   round2_questions_sent  → round2_intake_received → round2_synthesizing → round2_delivered
#   portrait_navigator_active

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path


BASE_DIR   = Path(__file__).parent
CLIENTS    = BASE_DIR / "clients"
PORTRAITS  = BASE_DIR / "portraits"
R2_QUESTIONS = BASE_DIR / "round2_questions"

VALID_TIERS  = {"standard", "deep", "full"}
VALID_STATES = [
    "round1_intake_received",
    "round1_synthesizing",
    "round1_delivered",
    "round2_questions_sent",
    "round2_intake_received",
    "round2_synthesizing",
    "round2_delivered",
    "portrait_navigator_active",
]

STATE_NEXT_ACTION = {
    "round1_intake_received": "Run intake_processor.py against round1 intake file",
    "round1_synthesizing":    "Wait for synthesis to complete, then mark round1_delivered",
    "round1_delivered":       "[Standard] Done. [Deep/Full] Run --generate-round2 then send questions",
    "round2_questions_sent":  "Wait for client to complete round2_form. Check email/intakes/ dir.",
    "round2_intake_received": "Run intake_processor.py against round2 intake file",
    "round2_synthesizing":    "Wait for synthesis to complete, then mark round2_delivered",
    "round2_delivered":       "[Full] Activate Portrait Navigator — share portrait_chat.html link with portrait embedded",
    "portrait_navigator_active": "Ongoing — client has active Navigator access for 90 days",
}


# ---------------------------------------------------------------------------
# Client file helpers
# ---------------------------------------------------------------------------
def name_to_slug(name: str) -> str:
    return name.lower().strip().replace(" ", "_")[:40]

def client_path(slug: str) -> Path:
    return CLIENTS / f"{slug}.json"

def load_client(slug: str) -> dict:
    p = client_path(slug)
    if not p.exists():
        print(f"ERROR: Client not found — {slug}")
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def save_client(slug: str, data: dict):
    CLIENTS.mkdir(exist_ok=True)
    data["updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(client_path(slug), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def all_clients() -> list:
    CLIENTS.mkdir(exist_ok=True)
    results = []
    for p in sorted(CLIENTS.glob("*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                results.append(json.load(f))
        except Exception:
            pass
    return results


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_list():
    clients = all_clients()
    if not clients:
        print("No clients yet. Use --new to add one.")
        return
    print(f"\n{'NAME':<25} {'TIER':<10} {'STATE':<35} {'CREATED'}")
    print("-" * 90)
    for c in clients:
        print(f"{c.get('name','?'):<25} {c.get('tier','?'):<10} {c.get('state','?'):<35} {c.get('created','?')}")
    print()


def cmd_status(slug: str):
    c = load_client(slug)
    print(f"\n{'='*50}")
    print(f"  CLIENT:  {c.get('name')}")
    print(f"  EMAIL:   {c.get('email')}")
    print(f"  TIER:    {c.get('tier')}")
    print(f"  STATE:   {c.get('state')}")
    print(f"  CREATED: {c.get('created')}")
    print(f"  UPDATED: {c.get('updated')}")
    if c.get('round1_portrait'): print(f"  R1 PORTRAIT: {c['round1_portrait']}")
    if c.get('round2_questions'): print(f"  R2 QUESTIONS: {c['round2_questions']}")
    if c.get('round2_intake'):    print(f"  R2 INTAKE: {c['round2_intake']}")
    if c.get('round2_portrait'):  print(f"  R2 PORTRAIT: {c['round2_portrait']}")
    print(f"{'='*50}\n")


def cmd_next_action(slug: str):
    c = load_client(slug)
    state = c.get("state", "unknown")
    action = STATE_NEXT_ACTION.get(state, f"Unknown state: {state}")
    print(f"\nClient: {c.get('name')} [{c.get('tier')}]")
    print(f"State:  {state}")
    print(f"Next:   {action}\n")

def cmd_generate_round2(slug: str):
    c = load_client(slug)
    tier = c.get("tier", "standard")
    if tier == "standard":
        print(f"ERROR: Client {slug} is on Standard tier — no Round 2 included.")
        sys.exit(1)

    portrait_file = c.get("round1_portrait")
    if not portrait_file:
        print("ERROR: No round1_portrait recorded for this client.")
        sys.exit(1)

    portrait_path = BASE_DIR / portrait_file if not Path(portrait_file).is_absolute() else Path(portrait_file)
    if not portrait_path.exists():
        print(f"ERROR: Portrait file not found at {portrait_path}")
        sys.exit(1)

    generator = BASE_DIR / "round2_generator.py"
    if not generator.exists():
        print("ERROR: round2_generator.py not found.")
        sys.exit(1)

    print(f"Generating Round 2 questions for {c.get('name')}...")
    result = subprocess.run([sys.executable, str(generator), str(portrait_path)],
                            capture_output=False, text=True)
    if result.returncode != 0:
        print("ERROR: round2_generator.py failed.")
        sys.exit(1)

    # Find the generated file
    date_slug = datetime.now().strftime("%Y%m%d")
    q_file = R2_QUESTIONS / f"{slug}_{date_slug}.md"
    if q_file.exists():
        c["round2_questions"] = str(q_file.relative_to(BASE_DIR))
        c["state"] = "round2_questions_sent"
        save_client(slug, c)
        print(f"\nState updated: round2_questions_sent")
        print(f"Questions at: {q_file}")
        print(f"Next: send this file to {c.get('name')} and share the round2_form.html link")
    else:
        print("NOTE: Could not auto-locate generated file. Update client JSON manually.")


def cmd_new(name: str, email: str, tier: str):
    if tier not in VALID_TIERS:
        print(f"ERROR: tier must be one of {VALID_TIERS}")
        sys.exit(1)
    slug = name_to_slug(name)
    CLIENTS.mkdir(exist_ok=True)
    if client_path(slug).exists():
        print(f"ERROR: Client already exists — {slug}")
        sys.exit(1)
    data = {
        "name": name,
        "email": email,
        "tier": tier,
        "state": "round1_intake_received",
        "round1_portrait": None,
        "round2_questions": None,
        "round2_intake": None,
        "round2_portrait": None,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "updated": datetime.now().strftime("%Y-%m-%d"),
    }
    save_client(slug, data)
    print(f"Client created: {slug}.json")
    print(f"  Name: {name} | Email: {email} | Tier: {tier}")
    print(f"  State: round1_intake_received")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("""
Thumbprint Coordinator — Portrait Lifecycle Tracker

Commands:
  --list                          Show all clients and states
  --status <slug>                 Show full status for one client
  --next-action <slug>            What needs to happen next for this client
  --generate-round2 <slug>       Generate personalized Round 2 questions
  --new <name> <email> <tier>     Create new client record
                                  (tier: standard | deep | full)

Examples:
  python autograph_coordinator.py --list
  python autograph_coordinator.py --status alex_rivera
  python autograph_coordinator.py --next-action alex_rivera
  python autograph_coordinator.py --generate-round2 alex_rivera
  python autograph_coordinator.py --new "Alex Rivera" alex@example.com deep
""")
        sys.exit(0)

    cmd = args[0]

    if cmd == "--list":
        cmd_list()
    elif cmd == "--status" and len(args) >= 2:
        cmd_status(args[1])
    elif cmd == "--next-action" and len(args) >= 2:
        cmd_next_action(args[1])
    elif cmd == "--generate-round2" and len(args) >= 2:
        cmd_generate_round2(args[1])
    elif cmd == "--new" and len(args) >= 4:
        cmd_new(args[1], args[2], args[3])
    else:
        print(f"ERROR: Unknown command or missing args: {' '.join(args)}")
        print("Run with --help for usage.")
        sys.exit(1)
