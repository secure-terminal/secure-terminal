# Pending AI reviews

Reviews that could not run because a cloud reviewer (codex) was unavailable /
rate-limited / timed out. Re-run each once the reviewer is available again,
ideally on a backoff timer (retry later, not in a tight loop), fold in any real
findings, and then DELETE the entry. Do NOT keep a log of completed reviews --
an empty "Open" list below means everything has been reviewed.

How to run one (see the `ai-review` skill):

    ai-review <range> --with codex --timeout 480 -- <paths...>

Prefer `--detach` for the longer ones, and re-run FOREGROUND with a single fast
reviewer if a detached run comes back empty.

## Open

(none)
