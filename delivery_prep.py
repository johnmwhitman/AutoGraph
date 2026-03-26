# Thumbprint Delivery Prep
# Takes a completed portrait .md file and produces a clean PDF (or .txt fallback)
# for client delivery.
#
# Usage:
#   python delivery_prep.py <portrait.md>
#   python delivery_prep.py --latest         (picks most recent file in portraits/)
#
# Output: AutoGraph_Portrait_{name}_{date}.pdf (or .txt) in portraits/

import os
import sys
from datetime import datetime
from pathlib import Path

PORTRAITS_DIR = Path(__file__).parent / "portraits"


def find_latest_portrait() -> Path:
    portraits = sorted(PORTRAITS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not portraits:
        print("ERROR: No portrait files found in portraits/")
        sys.exit(1)
    return portraits[0]


def parse_name_date_from_filename(p: Path):
    """Extract human-readable name + date slug from filename like alex_rivera_20260325.md"""
    stem  = p.stem  # e.g. alex_rivera_20260325
    parts = stem.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 8:
        raw_name  = parts[0].replace("_", " ").title()
        date_slug = parts[1]
    else:
        raw_name  = stem.replace("_", " ").title()
        date_slug = datetime.now().strftime("%Y%m%d")
    return raw_name, date_slug


def build_pdf(portrait_path: Path, out_path: Path, name: str, date_slug: str):
    """Render portrait markdown to PDF using reportlab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors

    text = portrait_path.read_text(encoding="utf-8")

    doc    = SimpleDocTemplate(str(out_path), pagesize=letter,
                               leftMargin=1.1*inch, rightMargin=1.1*inch,
                               topMargin=1.1*inch, bottomMargin=1.1*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("AG_Title",
        parent=styles["Heading1"], fontSize=18, spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"))
    h2_style    = ParagraphStyle("AG_H2",
        parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=4,
        textColor=colors.HexColor("#16213e"))
    body_style  = ParagraphStyle("AG_Body",
        parent=styles["Normal"], fontSize=10.5, leading=16,
        spaceAfter=8, textColor=colors.HexColor("#2d2d2d"))
    meta_style  = ParagraphStyle("AG_Meta",
        parent=styles["Normal"], fontSize=9, textColor=colors.grey, spaceAfter=12)

    story = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith("## "):
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#cccccc"), spaceAfter=4))
            story.append(Paragraph(line[3:], h2_style))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith("*") and line.endswith("*"):
            story.append(Paragraph(line.strip("*"), meta_style))
        elif line.startswith("**") and "**" in line[2:]:
            # bold inline — convert markdown bold to reportlab
            converted = line.replace("**", "<b>", 1).replace("**", "</b>", 1)
            story.append(Paragraph(converted, body_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)


def build_txt(portrait_path: Path, out_path: Path, name: str, date_slug: str):
    """
    Plain-text fallback when reportlab is not available.
    TODO: Install reportlab for proper PDF output: pip install reportlab
    """
    text = portrait_path.read_text(encoding="utf-8")
    header = (
        f"AutoGraph Behavioral Portrait\n"
        f"{'='*50}\n"
        f"Client: {name}\n"
        f"Date:   {date_slug}\n"
        f"{'='*50}\n\n"
    )
    out_path.write_text(header + text, encoding="utf-8")


if __name__ == "__main__":
    if "--latest" in sys.argv:
        portrait_path = find_latest_portrait()
        print(f"Using latest portrait: {portrait_path.name}")
    elif len(sys.argv) > 1:
        portrait_path = Path(sys.argv[1])
        if not portrait_path.exists():
            print(f"ERROR: File not found — {portrait_path}")
            sys.exit(1)
    else:
        print("Usage: python delivery_prep.py <portrait.md>")
        print("       python delivery_prep.py --latest")
        sys.exit(1)

    PORTRAITS_DIR.mkdir(exist_ok=True)
    name, date_slug = parse_name_date_from_filename(portrait_path)
    safe_name       = name.replace(" ", "_")

    try:
        out_path = PORTRAITS_DIR / f"Thumbprint_Portrait_{safe_name}_{date_slug}.pdf"
        build_pdf(portrait_path, out_path, name, date_slug)
        print(f"PDF portrait written to: {out_path}")
    except ImportError:
        out_path = PORTRAITS_DIR / f"Thumbprint_Portrait_{safe_name}_{date_slug}.txt"
        build_txt(portrait_path, out_path, name, date_slug)
        print(f"[reportlab not available — wrote .txt instead]")
        print(f"Delivery file written to: {out_path}")
        print("To enable PDF: pip install reportlab --break-system-packages")
    except Exception as e:
        print(f"ERROR during delivery prep: {e}")
        sys.exit(1)
