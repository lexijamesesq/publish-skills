#!/usr/bin/env python3
"""Shape guard for the six council cards.

Two receipts drive this. First, a reviewer that found nothing returned a bare
green tick with no record of what it examined — the unearnable green. Every card
must therefore carry a `Checked.` section telling the reviewer what its block has
to name. Second, card self-selection is retired: summoning is the driver's
Jev-decided routing now (which cards a change needs is scored per lens, recorded
in the route output), so a card no longer carries a self-selection heading and
`Stopping rule.` carries the probe budget.

This test pins the exact set of section headings a card may carry — presence of
every required one, and *nothing outside the allowed set*, so a retired heading
cannot creep back in under any name.

A card's tier is not asserted here on purpose: the card's model/tier is the
driver's council dispatch (it spawns each reviewer at the tier the routing
names), not the card's to declare — a `Tier:` line on a card would be a second
source. This test fails a card that reintroduces it.

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
    "**What you are given.**",
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
    "What you are given.",
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
    fail.append(
        f"playbooks/: card set is {sorted(names)}, expected {sorted(EXPECTED_CARDS)}"
    )

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
            fail.append(
                f"{rel}: carries a heading not in the allowed set: {m.group(1)!r}"
            )
    # the card's model/tier is the driver's council dispatch, not the card's
    for line in text.splitlines():
        if line.startswith("Tier:"):
            fail.append(
                f"{rel}: carries a 'Tier:' line — the driver's council dispatch is the tier source"
            )
    # a Checked section that doesn't ask for the detection target is not a probe rule
    checked = (
        text.split("**Checked.**", 1)[1].split("\n\n", 1)[0]
        if "**Checked.**" in text
        else ""
    )
    if "would have caught" not in checked and "would have detected" not in checked:
        fail.append(
            f"{rel}: the Checked section must ask for the failure each probe would have caught"
        )
    # the Findings section must carry the [issue|info] disposition-tag convention
    # (the clause axis SKILL.md defines) — so a card silently reverting to the old
    # bare `location · defect · consequence` shape is caught, not just the heading's
    # presence. Pins the six-card alignment the way test_schema.py pins SKILL.md.
    findings = text.split("**Findings.**", 1)[1] if "**Findings.**" in text else ""
    if "[issue|info]" not in findings and not (
        "[issue]" in findings and "[info]" in findings
    ):
        fail.append(
            f"{rel}: the Findings section must carry the [issue|info] disposition tag (SKILL.md's clause axis)"
        )

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print(
    f"OK: {len(CARDS)} council cards carry every required section, only allowed headings, a budget, and a Checked rule"
)
