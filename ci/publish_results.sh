#!/usr/bin/env bash
# Commit the collected results of this workflow run to the "results" branch, so they can be read (or cloned) without logging in.
#   bash ci/publish_results.sh <folder with the collected results>
set -euo pipefail
SRC=${1:?folder with the collected results}
RUN_DIR="runs/${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}"
WT=$(mktemp -d)/wt
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git fetch --no-tags origin results 2>/dev/null || true
if git rev-parse -q --verify refs/remotes/origin/results >/dev/null; then
  git worktree add -q -B results "$WT" refs/remotes/origin/results
else
  git worktree add -q --detach "$WT"
  git -C "$WT" checkout -q --orphan results
  git -C "$WT" rm -rfq --ignore-unmatch .
fi
mkdir -p "$WT/$RUN_DIR"
cp -R "$SRC"/. "$WT/$RUN_DIR"/
git -C "$WT" add -A
git -C "$WT" commit -q -m "Results of run ${GITHUB_RUN_ID:-local}"
for _ in 1 2 3 4 5; do
  if git -C "$WT" push -q origin HEAD:results; then echo "published to branch results: $RUN_DIR"; exit 0; fi
  git fetch --no-tags origin results
  git -C "$WT" rebase refs/remotes/origin/results
done
echo "could not push the results branch" >&2
exit 1
