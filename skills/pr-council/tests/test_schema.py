#!/usr/bin/env python3
"""Contract guard for the per-card result schema.

The first proof run's verdict crashed the poster: a field came back a string
where a structured value was expected, and no fenced schema existed anywhere for
the model to copy — the contract lived only as an inline prose key list. The
original fix fenced a copy of the AGGREGATE schema in agents/margot.md for the
model to emulate.

That copy is gone as of 0.1.23, and this test no longer requires it, because the
failure it guarded against no longer exists: Margot now reviews under `--agent`
and a downstream no-tool `claude -p --json-schema` "finalize" call transcribes
her review into the verdict. `--json-schema` HARD-enforces the shape via
constrained decoding against dotty-private's verdict.schema.json — the model
cannot return a string where a structured value belongs, so no copy-for-the-model
is needed and none is carried (see the slim in agents/margot.md). The aggregate
schema is now single-homed in dotty-private (verdict.schema.json + the poster's
render tests); AGGREGATE_KEYS below is retained as the documented cross-repo
reference, no longer asserted against a margot.md block on this side.

What this still pins:

  * the PER-CARD result, in skills/pr-council/SKILL.md — what one reviewer
    returns to Margot. Unchanged by Plan B: pr-reviewers still emit this shape.

Usage: python3 skills/pr-council/tests/test_schema.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "pr-council" / "SKILL.md"

# Documented cross-repo reference only (no longer asserted on this side): the
# aggregate verdict schema is single-homed in dotty-private's verdict.schema.json,
# which finalize's constrained decoding enforces and the poster's render tests pin.
AGGREGATE_KEYS = [
    "outcome", "risk", "risk_reason", "rationale", "authority", "clarification",
    "summoned", "not_summoned", "checked", "findings", "dismissals", "ticket",
]
PER_CARD_KEYS = ["reviewer", "completion", "checked", "not_covered", "findings"]
PER_CARD_FINDING_KEYS = [
    "reviewer", "clause", "severity", "confidence", "location", "sentence",
    "consequence", "action",
]
CARD_NAMES = [
    "house-style", "works-and-proven", "achieves-the-objective",
    "maintainable-no-slop", "principal-engineer", "safety",
]

fail = []


def fenced_json(path):
    """Return every ```json block in path, parsed. A block that won't parse is a failure."""
    blocks = re.findall(r"```json\n(.*?)\n```", path.read_text(), re.DOTALL)
    out = []
    for i, b in enumerate(blocks):
        try:
            out.append(json.loads(b))
        except json.JSONDecodeError as e:
            fail.append(f"{path.relative_to(ROOT)}: fenced json block {i} does not parse: {e}")
    return out


card_blocks = fenced_json(SKILL)

if len(card_blocks) != 1:
    fail.append(f"pr-council/SKILL.md: expected exactly 1 fenced json schema, found {len(card_blocks)}")

if card_blocks:
    card = card_blocks[0]
    if list(card) != PER_CARD_KEYS:
        fail.append(f"pr-council/SKILL.md: per-card keys are {list(card)}, expected {PER_CARD_KEYS}")
    # a green card is earnable only through its Checked list
    if not isinstance(card.get("checked"), list) or not card.get("checked"):
        fail.append("pr-council/SKILL.md: checked must be a non-empty list of probes")
    if not isinstance(card.get("not_covered"), list):
        fail.append("pr-council/SKILL.md: not_covered must be a list")
    cf = (card.get("findings") or [{}])[0]
    if list(cf) != PER_CARD_FINDING_KEYS:
        fail.append(f"pr-council/SKILL.md: finding keys are {list(cf)}, expected {PER_CARD_FINDING_KEYS}")

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print("OK: the per-card fenced schema parses and carries exactly its pinned keys")
