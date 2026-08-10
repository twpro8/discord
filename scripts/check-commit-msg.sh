#!/usr/bin/env bash
set -euo pipefail

commit_msg_file="$1"
subject="$(head -n1 "$commit_msg_file")"

# Merge commits aren't authored by contributors typing a subject line - skip them.
if [[ "$subject" == Merge\ * ]]; then
    exit 0
fi

pattern='^(feat|fix|chore|docs|test|refactor|style|perf|build|ci|revert)(\([^)]+\))?!?: .+'

if [[ ! "$subject" =~ $pattern ]]; then
    echo "Commit message must follow Conventional Commits: <type>(<scope>)?!?: <description>" >&2
    echo "  types: feat fix chore docs test refactor style perf build ci revert" >&2
    echo "  got:   $subject" >&2
    exit 1
fi
