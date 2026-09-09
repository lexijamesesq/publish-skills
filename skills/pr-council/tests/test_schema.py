#!/usr/bin/env python3
"""Contract guard for the two result schemas.

The first proof run's verdict crashed the poster: `completion` came back a string
where a dict was expected, and no fenced schema existed anywhere for the model to
copy — the contract lived only as an inline prose key list. Both schemas are now
fenced at their producer, and this test pins them:

  * the AGGREGATE, in agents/margot.md — the object Margot returns and a
    deterministic poster reads.
  * the PER-CARD result, in skills/pr-council/SKILL.md — what one reviewer
    returns to Margot.

The literal key lists below are this side of a cross-repo anchor. A test in this
repository cannot read the poster that consumes the aggregate, so the runtime
slice adds a fixture mirroring THIS list on the poster's side. Until it does, the
keys are pinned here only, and a rename that crosses the repo boundary is caught
by nothing.

Usage: python3 skills/pr-council/tests/test_schema.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
MARGOT = ROOT / "agents" / "margot.md"
SKILL = ROOT / "skills" / "pr-council" / "SKILL.md"

AGGREGATE_KEYS = [
    "verdict", "risk", "risk_reason", "rationale", "author_action", "surface",
    "findings", "skips", "completion", "checked", "ticket",
]
AGGREGATE_FINDING_KEYS = [
    "reviewers", "clause", "location", "sentence", "severity", "confidence",
    "consequence", "action",
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


agg_blocks = fenced_json(MARGOT)
card_blocks = fenced_json(SKILL)

if len(agg_blocks) != 1:
    fail.append(f"agents/margot.md: expected exactly 1 fenced json schema, found {len(agg_blocks)}")
if len(card_blocks) != 1:
    fail.append(f"pr-council/SKILL.md: expected exactly 1 fenced json schema, found {len(card_blocks)}")

if agg_blocks:
    agg = agg_blocks[0]
    if list(agg) != AGGREGATE_KEYS:
        fail.append(f"agents/margot.md: aggregate keys are {list(agg)}, expected {AGGREGATE_KEYS}")
    # the poster builds its per-card lines from findings[].reviewers as a LIST —
    # a finding carrying a bare `reviewer` string is silently dropped from them
    finding = (agg.get("findings") or [{}])[0]
    if not isinstance(finding.get("reviewers"), list):
        fail.append("agents/margot.md: findings[].reviewers must be a list")
    if list(finding) != AGGREGATE_FINDING_KEYS:
        fail.append(f"agents/margot.md: finding keys are {list(finding)}, expected {AGGREGATE_FINDING_KEYS}")
    # completion is a dict card -> status. The contract is that only 'completed'
    # renders green; the poster's own else-branch still paints an incomplete card
    # green until the runtime slice fixes it, so this pins the shape, not that rule.
    comp = agg.get("completion")
    if not isinstance(comp, dict):
        fail.append("agents/margot.md: completion must be a dict of card name to status")
    elif sorted(comp) != sorted(CARD_NAMES):
        fail.append(f"agents/margot.md: completion names {sorted(comp)}, expected {sorted(CARD_NAMES)}")
    # checked is the only carrier that gets the six Checked blocks into the run log
    if not isinstance(agg.get("checked"), dict):
        fail.append("agents/margot.md: checked must be a dict of card name to probe list")
    skip = (agg.get("skips") or [{}])[0]
    if sorted(skip) != ["reason", "reviewer"]:
        fail.append(f"agents/margot.md: skips[] keys are {sorted(skip)}, expected ['reason', 'reviewer']")
    if not isinstance(agg.get("ticket"), dict) or "id" not in (agg.get("ticket") or {}):
        fail.append("agents/margot.md: ticket must be an object carrying an id")

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
print("OK: both fenced schemas parse and carry exactly their pinned keys")
