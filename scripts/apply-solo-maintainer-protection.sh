#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/apply-solo-maintainer-protection.sh [--owner OWNER] [--repo OWNER/NAME ...] [--branch BRANCH] [--apply]

Harmonize GitHub branch protection for a solo maintainer.

Default mode is dry-run. With --apply, the script only changes the pull-request
review protection subresource on already protected branches:

  required_approving_review_count = 0
  require_code_owner_reviews      = false
  dismiss_stale_reviews           = true
  require_last_push_approval      = false

It intentionally preserves required status checks, force-push/deletion blocks,
conversation-resolution settings, and other branch protection controls.

Examples:
  scripts/apply-solo-maintainer-protection.sh
  scripts/apply-solo-maintainer-protection.sh --apply
  scripts/apply-solo-maintainer-protection.sh --repo constantin-jais/rumble-feed-mind --apply
USAGE
}

owner="constantin-jais"
branch_override=""
apply=0
repos=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner)
      owner="${2:?--owner requires a value}"
      shift 2
      ;;
    --repo)
      repos+=("${2:?--repo requires OWNER/NAME}")
      shift 2
      ;;
    --branch)
      branch_override="${2:?--branch requires a value}"
      shift 2
      ;;
    --apply)
      apply=1
      shift
      ;;
    --dry-run)
      apply=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 127
  fi
}

require_cmd gh
require_cmd jq

repo_rows() {
  if [[ ${#repos[@]} -gt 0 ]]; then
    for repo in "${repos[@]}"; do
      local branch="$branch_override"
      if [[ -z "$branch" ]]; then
        branch=$(gh repo view "$repo" --json defaultBranchRef --jq '.defaultBranchRef.name')
      fi
      printf '%s\t%s\n' "$repo" "$branch"
    done
    return
  fi

  gh repo list "$owner" \
    --limit 200 \
    --json nameWithOwner,isArchived,isFork,defaultBranchRef \
    --jq '.[] | select(.isArchived == false and .isFork == false and .defaultBranchRef.name != null) | [.nameWithOwner, .defaultBranchRef.name] | @tsv'
}

patch_payload='{
  "dismiss_stale_reviews": true,
  "require_code_owner_reviews": false,
  "required_approving_review_count": 0,
  "require_last_push_approval": false
}'

mode="dry-run"
if [[ "$apply" -eq 1 ]]; then
  mode="apply"
fi

echo "mode=$mode owner=$owner"

while IFS=$'\t' read -r repo branch; do
  [[ -n "$repo" && -n "$branch" ]] || continue
  echo "### $repo ($branch)"

  protection=$(gh api "repos/$repo/branches/$branch/protection" 2>/dev/null || true)
  if [[ -z "$protection" ]]; then
    echo "skip: branch has no classic protection or token cannot read it"
    continue
  fi

  if ! jq -e '.required_pull_request_reviews != null' >/dev/null <<<"$protection"; then
    echo "skip: no pull-request review protection to harmonize"
    continue
  fi

  before=$(jq -c '.required_pull_request_reviews | {required_approving_review_count, require_code_owner_reviews, dismiss_stale_reviews, require_last_push_approval}' <<<"$protection")
  checks=$(jq -r '(.required_status_checks.contexts // []) | join(",")' <<<"$protection")
  echo "before=$before"
  echo "preserve_checks=${checks:-none}"

  if [[ "$apply" -ne 1 ]]; then
    echo "would_apply=$patch_payload"
    continue
  fi

  after=$(jq -n "$patch_payload" \
    | gh api -X PATCH "repos/$repo/branches/$branch/protection/required_pull_request_reviews" --input - \
      --jq '{required_approving_review_count, require_code_owner_reviews, dismiss_stale_reviews, require_last_push_approval}')
  echo "after=$after"
done < <(repo_rows)
