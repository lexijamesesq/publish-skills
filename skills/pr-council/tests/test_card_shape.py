#!/usr/bin/env python3
"""Shape guard for the six council cards.

Two receipts drive this. First, a reviewer that found nothing returned a bare
green tick with no record of what it examined — the unearnable green. Every card
must therefore carry a `Checked.` section telling the reviewer what its block has
to name. Second, card self-selection is retired: summoning is Margot's judgment
now (`agents/margot.md`), recorded as `not summoned: <fact>`, so a card no longer
carries a self-selection heading and `Stopping rule.` carries the probe budget.

This test pins the exact set of section headings a card may carry — presence of
every required one, and *nothing outside the allowed set*, so a retired heading
cannot creep back in under any name.

A card's tier is not asserted here on purpose: the tier table lives in
agents/margot.md as the single source, and a `Tier:` line on a card would be a
second one. This test fails a card that reintroduces it.

Usage: python3 skills/pr-council/tests/test_card_shape.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CARDS = sorted((ROOT / "skills" / "pr-council" / "playbooks").glob("*.md"))

# Required sections, in the order a card presents them. `*Remit:` is the italic
# one-line remit; the rest are bold section headings.
REQUIRED = [
    "*Remit:",
    "**What Margot gives you.**",
    "**Fetch your own evidence.**",
    "**Insists on**",
    "**Flags**",
    "**Never.**",
    "**Stopping rule.**",
    "**Checked.**",
    "**Findings.**",
]

# The closed set of bold section headings a card may carry. A heading starts a
# paragraph — a line-start `**…**` whose previous line is blank — so a stray or
# reintroduced section is caught, while inline bold at the start of a *wrapped*
# line (previous line non-blank) is correctly not treated as a heading.
ALLOWED_HEADINGS = {
    "What Margot gives you.",
    "Fetch your own evidence.",
    "Insists on",
    "Flags",
    "Never.",
    "Stopping rule.",
    "Checked.",
    "Findings.",
}
HEADING = re.compile(r"^\*\*(.+?)\*\*")

EXPECTED_CARDS = {
    "achieves-the-objective",
    "house-style",
    "maintainable-no-slop",
    "principal-engineer",
    "safety",
    "works-and-proven",
}

fail = []

names = {p.stem for p in CARDS}
if names != EXPECTED_CARDS:
    fail.append(f"playbooks/: card set is {sorted(names)}, expected {sorted(EXPECTED_CARDS)}")

for p in CARDS:
    text = p.read_text()
    rel = p.relative_to(ROOT)
    for section in REQUIRED:
        if section not in text:
            fail.append(f"{rel}: missing required section {section!r}")
    # nothing outside the allowed heading set — catches a retired section coming
    # back. A heading starts a paragraph, so the line before it is blank; this
    # skips inline bold at the start of a wrapped line.
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        prev_blank = i == 0 or lines[i - 1].strip() == ""
        if m and prev_blank and m.group(1) not in ALLOWED_HEADINGS:
            fail.append(f"{rel}: carries a heading not in the allowed set: {m.group(1)!r}")
    # the tier table in agents/margot.md is the single source
    for line in text.splitlines():
        if line.startswith("Tier:"):
            fail.append(f"{rel}: carries a 'Tier:' line — the tier table in agents/margot.md is the source")
    # a Checked section that doesn't ask for the detection target is not a probe rule
    checked = text.split("**Checked.**", 1)[1].split("\n\n", 1)[0] if "**Checked.**" in text else ""
    if "would have caught" not in checked and "would have detected" not in checked:
        fail.append(f"{rel}: the Checked section must ask for the failure each probe would have caught")

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print(f"OK: {len(CARDS)} council cards carry every required section, only allowed headings, a budget, and a Checked rule")
