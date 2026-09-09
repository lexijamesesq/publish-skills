#!/usr/bin/env python3
"""Shape guard for the six council cards.

Two receipts drive this. First, a reviewer that found nothing returned a bare
green tick with no record of what it examined — the unearnable green. Every card
must therefore carry a `Checked.` section telling the reviewer what its block has
to name. Second, every card's `Stopping rule.` heading held a SKIP rule, so the
probe budget read as present on a skim while no card capped anything; the skip
rule is now `Skip rule.` and `Stopping rule.` carries the budget.

A card's tier is not asserted here on purpose: the tier table lives in
agents/margot.md as the single source, and a `Tier:` line on a card would be a
second one. This test fails a card that reintroduces it.

Usage: python3 skills/pr-council/tests/test_card_shape.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CARDS = sorted((ROOT / "skills" / "pr-council" / "playbooks").glob("*.md"))

REQUIRED = [
    "*Remit:",
    "**What Margot gives you.**",
    "**Fetch your own evidence.**",
    "**Insists on**",
    "**Flags**",
    "**Never.**",
    "**Skip rule.**",
    "**Stopping rule.**",
    "**Checked.**",
    "**Findings.**",
]

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
print(f"OK: {len(CARDS)} council cards carry every required section, a budget, and a Checked rule")
