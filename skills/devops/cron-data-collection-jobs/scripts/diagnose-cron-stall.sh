#!/usr/bin/env bash
# Diagnose a Hermes cron job that appears stuck (Execution: running) —
# find whether it stalled on safety BLOCKED or missing web_search provider.
# Usage: diagnose-cron-stall.sh <job_id>
set -u

JOB_ID="${1:?usage: diagnose-cron-stall.sh <job_id>}"
LOG="${HOME}/.hermes/logs/errors.log"

echo "== cron runs for ${JOB_ID} =="
hermes cron runs "${JOB_ID}" 2>&1 | tail -8

if [ ! -f "${LOG}" ]; then
  echo "errors.log not found at ${LOG} — nothing to scan."
  exit 0
fi

echo
echo "== recent session lines for cron_${JOB_ID}_ in errors.log =="
grep "cron_${JOB_ID}_" "${LOG}" | tail -20 || echo "(no lines for this job)"

echo
echo "== stall signatures =="
grep "cron_${JOB_ID}_" "${LOG}" \
  | grep -E "BLOCKED|No web search provider configured|pending_approval|approval_pending" \
  | tail -10 \
  || echo "(no BLOCKED / web_search / pending_approval hits — check other causes: 401, import error, iteration limit)"
