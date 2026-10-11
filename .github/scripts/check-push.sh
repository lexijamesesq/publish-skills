#!/usr/bin/env bash
# Select native outgoing paths, including deletions and both rename sides.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
component=${1:?usage: check-push.sh plugin | council}
case "$component" in plugin | council) ;; *)
	echo "Unknown component: $component" >&2
	exit 2
	;;
esac
paths=$(mktemp)
trap 'rm -f "$paths"' EXIT
if [[ -n "${PRE_COMMIT_FROM_REF:-}" && -n "${PRE_COMMIT_TO_REF:-}" ]]; then
	outgoing=$PRE_COMMIT_TO_REF
	git diff --name-only --no-renames -z "$PRE_COMMIT_FROM_REF" "$PRE_COMMIT_TO_REF" >"$paths"
elif [[ -n "${PRE_COMMIT_REMOTE_NAME:-}" && -n "${PRE_COMMIT_LOCAL_BRANCH:-}" ]]; then
	outgoing=$PRE_COMMIT_LOCAL_BRANCH
	git rev-parse --verify "$PRE_COMMIT_LOCAL_BRANCH^{commit}" >/dev/null
	git log --format= --name-only --no-renames -z "$PRE_COMMIT_LOCAL_BRANCH" --not "--remotes=$PRE_COMMIT_REMOTE_NAME" >"$paths"
else
	echo 'Cannot select push checks: native outgoing range is unavailable.' >&2
	exit 2
fi
relevant=false
while IFS= read -r -d '' path; do
	path=${path#$'\n'}
	case "$path" in .pre-commit-config.yaml | .github/scripts/check-push.sh) relevant=true ;; esac
	case "$component:$path" in
	plugin:.claude-plugin/* | plugin:skills/* | plugin:agents/* | plugin:commands/* | plugin:hooks/* | plugin:.mcp.json | plugin:.lsp.json | plugin:settings.json | plugin:package.json | plugin:package-lock.json) relevant=true ;;
	council:skills/pr-council/* | council:agents/pr-reviewer.md | council:agents/margot.md | council:pyproject.toml | council:requirements*.txt | council:uv.lock) relevant=true ;;
	esac
done <"$paths"
[[ "$relevant" == true ]] || {
	echo "$component: no affected inputs"
	exit 0
}
outgoing=$(git rev-parse --verify "$outgoing^{commit}") || exit 2
head=$(git rev-parse --verify HEAD) || exit 2
untracked=$(git ls-files --others --exclude-standard) || exit 2
if [[ "$outgoing" != "$head" ]] || ! git diff --quiet "$outgoing" -- ||
	! git diff --cached --quiet "$outgoing" -- || [[ -n "$untracked" ]]; then
	echo 'BLOCKED: push checks require a clean checkout at the pushed head (including index and nonignored untracked files).' >&2
	exit 2
fi
case "$component" in
plugin) claude plugin validate --strict . ;;
council)
	for suite in confinement card_shape schema; do
		PYTHONDONTWRITEBYTECODE=1 python3 -B "skills/pr-council/tests/test_${suite}.py"
	done
	;;
esac
