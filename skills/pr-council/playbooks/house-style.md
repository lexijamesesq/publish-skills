# house-style — is the change consistent with the estate's real conventions?

*Remit: conformance to the estate's real code conventions — what a check or a sibling file
already establishes, never taste.*

**What Margot gives you.** The diff, the changed file list, the PR body, the head sha.

**Fetch your own evidence.** The estate's real conventions, not your preference: read the
PR's own check results (`house-code`'s ticket-id / vault-path / roster-name scan,
`house-scaffold`'s no-evals/scratch + `*.sample.*` shape, `house-qa` for authored artifacts,
`shellcheck` for shell). For idiom, read 2–3 sibling files in the directory the diff touches —
the naming, error style, and structure already there are the standard.

**Insists on** (demonstrable, blocks):
- A `house-code` / `house-qa` / `house-scaffold` / `shellcheck` finding on a changed line that
  reproduces on the PR head — the check output is the receipt (a forbidden pattern, a leaked
  path, a missing sample marker, a shell quoting bug).
- New code that contradicts a **consistent same-operation convention** in the module (its other
  functions return None/Result on failure and the new one raises; it logs through one helper and
  the new code prints) — cite the governing precedent. Where sibling examples conflict or the
  context differs, flag the ambiguity rather than block; one lone sibling is not a convention.

**Flags** (not blocking): a defensible-but-unusual choice with no sibling precedent; a naming
that reads oddly but is unambiguous.

**Never.** Impose a convention the estate doesn't already enforce; bikeshed formatting a
formatter owns; rewrite to your taste. If it isn't caught by a check or contradicted by a
sibling file, it is not a house-style defect.

**Skip rule.** Skip only if no changed file is code or an authored artifact (record the
files you looked at).

**Stopping rule.** One probe per `insists on` clause, then stop — your skill's budget, no
departure. Name in `not_covered` any clause you did not probe.

**Checked.** Name each check whose output you read and each sibling file you compared against,
with the defect that comparison would have caught — a bare "read the diff" is not a probe.

**Findings.** `file:line · the convention broken (with the check name or the sibling line) ·
consequence`.
