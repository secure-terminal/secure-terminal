## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

"""Session persistence: the open tabs and their scrollback, so they survive a
restart or reboot.

Stored under the XDG state directory (~/.local/state/secure-terminal/session.json)
because it is restorable session state, not configuration. JSON is used rather
than the KEY=value settings format because a tab's scrollback is multi-line
text; json.load runs no code, so it stays safe to parse. Loading is defensive: a
missing or malformed file yields an empty session and never crashes.

A running program (bash, nano, ...) cannot be resurrected -- only the tab list,
each tab's name/colour/settings and its (already sanitized, ASCII) scrollback are
saved, and a fresh shell starts under the restored history.
"""

import os
import json

# A hard cap on the persisted scrollback of an "unlimited" tab, so the session
# file cannot grow without bound on disk even when no line limit is set.
UNLIMITED_PERSIST_LINES = 5000


def _state_dir():
    base = os.environ.get('XDG_STATE_HOME') or os.path.join(
        os.path.expanduser('~'), '.local', 'state')
    return os.path.join(base, 'secure-terminal')


def session_path():
    return os.path.join(_state_dir(), 'session.json')


def cap_text(text, scrollback):
    """Trim scrollback text to the tab's line limit (or the hard cap when the
    tab is unlimited), keeping the most recent lines."""
    limit = scrollback if scrollback > 0 else UNLIMITED_PERSIST_LINES
    lines = text.split('\n')
    if len(lines) > limit:
        lines = lines[-limit:]
    return '\n'.join(lines)


def save(tabs):
    """Write the list of tab dicts. Never raises."""
    path = session_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as handle:
            json.dump({'tabs': tabs}, handle)
        os.replace(tmp, path)
    except OSError:
        pass                    # a failed session save is never fatal


def load():
    """Return the list of saved tab dicts, or []. Never raises."""
    try:
        with open(session_path(), encoding='utf-8') as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return []               # no/corrupt session -> start fresh
    tabs = data.get('tabs') if isinstance(data, dict) else None
    return tabs if isinstance(tabs, list) else []


def clear():
    """Remove the saved session. Never raises."""
    try:
        os.remove(session_path())
    except OSError:
        pass                    # nothing saved -> nothing to clear
