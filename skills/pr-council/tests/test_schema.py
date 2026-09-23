#!/usr/bin/env python3
"""Contract guard for the per-card council result — now a PROSE convention.

History: the per-card result was once a fenced JSON object (reviewer/completion/
checked/not_covered/findings) that a downstream `claude -p --json-schema` "finalize"
call transcribed into dotty-private's aggregate verdict.schema.json. The Margot
re-architecture removes finalize and moves the typing to the decision seam (Jev,
or a Haiku-with-schema bridge); no `--agent` output is transcribed. So
the council reviewer now returns a **stated prose convention** — an [issue]/[info]
disposition tag with severity + confidence as parallel fields — that the
deterministic driver and the decision seam parse leniently, not a constrained-typed
JSON object.

This test pins that convention's copyable shape in skills/pr-council/SKILL.md:
exactly one fenced shape block carrying the emitted lines, and NO per-card JSON
object left lingering. A future edit that paraphrases the shape into prose (losing
the copyable block) breaks this test on purpose — the copyable shape was the value
the JSON block used to carry.

The AGGREGATE verdict schema is single-homed in dotty-private (verdict.schema.json
+ the poster's render tests); AGGREGATE_KEYS below is retained only as a documented
cross-repo reference. NOTE: finalize + every verdict.schema.json copy are DELETED at
the finalize-removal slice of the re-architecture — this aggregate reference retires
with them.

Usage: python3 skills/pr-council/tests/test_schema.py
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "pr-council" / "SKILL.md"

# Documented cross-repo reference only (retires at S4 with finalize).
AGGREGATE_KEYS = [
    "outcome",
    "risk",
    "risk_reason",
    "rationale",
    "authority",
    "clarification",
    "summoned",
    "not_summoned",
    "checked",
    "findings",
    "dismissals",
    "ticket",
]

# The emitted prose-convention markers the copyable shape block must carry.
SHAPE_MARKERS = [
    "card:",
    "completion:",
    "Checked:",
    "Not covered:",
    "Findings:",
    "[issue]",
    "[info]",
    "severity=",
    "confidence=",
    "what:",
    "consequence:",
    "action:",
    "note:",
]
# JSON string-keys of the RETIRED per-card object — none may linger.
RETIRED_JSON_KEYS = ['"reviewer"', '"completion"', '"not_covered"']

fail = []
text = SKILL.read_text()

# Every fenced block as (info-string, body).
fences = re.findall(r"```([^\n]*)\n(.*?)\n```", text, re.DOTALL)

# 1. No per-card JSON object survives.
json_blocks = [body for info, body in fences if info.strip() == "json"]
if json_blocks:
    fail.append(
        f"pr-council/SKILL.md: found {len(json_blocks)} fenced ```json block(s); the "
        "per-card result is a prose convention now — no JSON object should remain"
    )
for k in RETIRED_JSON_KEYS:
    if k in text:
        fail.append(f"pr-council/SKILL.md: retired per-card JSON key {k} still present")

# 2. Exactly one copyable shape block (a ```text fence) carries the convention.
shape_blocks = [
    body
    for info, body in fences
    if info.strip() == "text" and "card:" in body and "Findings:" in body
]
if len(shape_blocks) != 1:
    fail.append(
        "pr-council/SKILL.md: expected exactly 1 copyable shape block (a ```text fence "
        f"containing 'card:' and 'Findings:'), found {len(shape_blocks)}"
    )
else:
    block = shape_blocks[0]
    for marker in SHAPE_MARKERS:
        if marker not in block:
            fail.append(
                f"pr-council/SKILL.md: the shape block is missing the marker {marker!r}"
            )

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print(
    "OK: the per-card prose convention is single-homed and carries its copyable shape"
)
