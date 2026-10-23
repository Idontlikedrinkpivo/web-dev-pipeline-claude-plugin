"""dev-pipeline: find what looks like a secret in the user's message — by its shape, never echoing it.

Reads the UserPromptSubmit hook input (JSON on stdin, its `prompt` field) and, when a shape below matches, prints the
hook output that adds one instruction for the model: the kinds found, never the values (pipeline → Secrets). Prints
nothing otherwise. Python 3.9+, standard library only; never fails the session.
"""
from __future__ import annotations

import json
import re
import sys

SHAPES = [  # (kind, the variable name it usually lives in, pattern)
    ("ключ Anthropic", "ANTHROPIC_API_KEY", r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    ("ключ OpenAI", "OPENAI_API_KEY", r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}"),
    ("ключ Stripe", "STRIPE_SECRET_KEY", r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}"),
    ("токен GitHub", "GITHUB_TOKEN", r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{22,})"),
    ("ключ AWS", "AWS_ACCESS_KEY_ID", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("ключ Google", "GOOGLE_API_KEY", r"\b(?:AIza[0-9A-Za-z_-]{35}|ya29\.[0-9A-Za-z_-]{20,})"),
    ("токен Slack", "SLACK_BOT_TOKEN", r"\bxox[abprs]-[0-9A-Za-z-]{10,}"),
    ("токен Telegram-бота", "TELEGRAM_BOT_TOKEN", r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"),
    ("токен Figma", "FIGMA_TOKEN", r"\bfigd_[A-Za-z0-9_-]{20,}"),
    ("токен Яндекса", "YANDEX_OAUTH_TOKEN", r"\by0_[A-Za-z0-9_-]{30,}"),
    ("JWT", "JWT_SECRET", r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ("строка подключения с паролем", "DATABASE_URL", r"\b[a-z][a-z0-9+.-]{1,20}://[^\s:/@]+:[^\s@/]{3,}@[^\s/]+"),
    ("закрытый ключ", "PRIVATE_KEY", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    # a long random-looking value right after a word that names a secret; a rule about passwords
    # («пароль не короче 8 символов») has no such value and does not match
    ("ключ или пароль", "<ИМЯ>_SECRET",
     r"(?i)(?:key|token|secret|password|passwd|ключ|токен|секрет|пароль)[^\n]{0,20}?[:=\s]"
     r"(?=[A-Za-z0-9+/_=-]{24,})(?=[^\s]*\d)(?=[^\s]*[A-Za-z])[A-Za-z0-9+/_=-]{24,}"),
]


def kinds(text: str) -> list:
    found = []
    for kind, var, rx in SHAPES[:-1]:
        if re.search(rx, text) and (kind, var) not in found:
            found.append((kind, var))
    kind, var, rx = SHAPES[-1]  # the generic shape only when no named one explains the message
    return found or ([(kind, var)] if re.search(rx, text) else [])


def main() -> None:
    try:
        prompt = str(json.load(sys.stdin).get("prompt") or "")
    except (ValueError, AttributeError):
        return
    hits = kinds(prompt)
    if not hits:
        return
    names = "; ".join(f"{k} → {v}" for k, v in hits)
    note = ("dev-pipeline: the user's message contains what looks like a secret (" + names + "; the values are not "
            "repeated here). Never repeat, quote or store the value — not in a document, an agent's packet, a commit, "
            "a progress file, a command you run or your reply. Refer to it by its variable name; where the project "
            "needs it, `.env.example` gets the name with an empty value and the user writes the value into the "
            "git-ignored `.env` themselves. Tell the user in one plain Russian line that the value was not saved, and "
            "that it is worth revoking and issuing a new one, since it has been in the chat (pipeline → Secrets). "
            "Then go on with what they asked.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": note}},
                     ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a broken scan must never block the user's message
        pass
