#!/usr/bin/env python3
"""Refresh derived question blocks in a BRD from its adjacent canonical register.

    python3 question_projection.py business-requirements.md [--check]

Place <!-- ce-question-include: OQ-7; level: 3 --> followed by
<!-- /ce-question-include --> at the relevant topic. Never edit the generated
body. Source: adjacent open-questions.md with ce-question markers followed by
numbered question headings. --check detects stale text without writing.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sys

OPEN = re.compile(r'<!-- ce-question-include: (OQ-\d+)(?:; level: ([2-6]))? -->')
CLOSE = '<!-- /ce-question-include -->'
QUESTION = re.compile(r'<!-- ce-question: (OQ-\d+)(?:;[^\n]*?)? -->')
HEADING = re.compile(r'^(#{1,6}) ([^\n]+)$', re.M)


def questions(text: str) -> dict[str, str]:
    """Keep canonical wording, options and classifications; never invent a decision."""
    markers = list(QUESTION.finditer(text))
    result = {}
    for i, marker in enumerate(markers):
        key = marker[1]
        if key in result:
            raise ValueError(f'duplicate canonical question: {key}')
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        body = text[marker.end():end]
        heading = HEADING.search(body)
        if not heading or body[:heading.start()].strip():
            raise ValueError(f'{key}: expected a question heading immediately after its marker')
        # A subsequent heading at the same or higher level ends the question.
        for following in HEADING.finditer(body, heading.end()):
            if len(following[1]) <= len(heading[1]):
                body = body[:following.start()]
                break
        result[key] = (marker.group().replace('ce-question:', 'ce-question-ref:', 1)
                       + '\n' + body.strip())
    return result


def project(document: str, register: str) -> str:
    starts = list(OPEN.finditer(document))
    if len(starts) != document.count(CLOSE) or len(starts) != document.count('<!-- ce-question-include:'):
        raise ValueError('unmatched or malformed question include markers')
    known = questions(register)
    pieces = []; offset = 0; seen = set()
    for marker in starts:
        key = marker[1]
        if marker.start() < offset:
            raise ValueError('nested question include markers')
        end = document.find(CLOSE, marker.end())
        if end < 0 or CLOSE in document[offset:marker.start()]:
            raise ValueError('unmatched question include markers')
        if key in seen:
            raise ValueError(f'include each question once, link to it elsewhere: {key}')
        seen.add(key)
        if key not in known:
            raise ValueError(f'{key}: missing canonical ce-question block in open-questions.md')
        body = known[key]
        heading = HEADING.search(body)
        assert heading is not None
        old = len(heading[1]); target = int(marker[2] or '3')
        def shift(match):
            depth = len(match[1]) + target - old
            if not 1 <= depth <= 6:
                raise ValueError(f'{key}: heading nesting exceeds Markdown levels')
            return '#' * depth + ' ' + match[2]
        body = HEADING.sub(shift, body)
        pieces += [document[offset:marker.end()], '\n\n', body, '\n\n', CLOSE]
        offset = end + len(CLOSE)
    pieces.append(document[offset:])
    return ''.join(pieces)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        original = args.document.read_text(encoding='utf-8')
        if '<!-- ce-question-include:' not in original and CLOSE not in original:
            print('no question projections'); return 0
        canonical = args.document.with_name('open-questions.md').read_text(encoding='utf-8')
        updated = project(original, canonical)
        if args.check and original != updated:
            print('stale question projections: refresh before presenting the document', file=sys.stderr)
            return 1
        if not args.check and original != updated:
            args.document.write_text(updated, encoding='utf-8')
        print('question projections: current' if original == updated else 'question projections: refreshed')
        return 0
    except (OSError, ValueError) as error:
        print(f'question_projection: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
