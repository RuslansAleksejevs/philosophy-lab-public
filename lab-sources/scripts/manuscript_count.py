#!/usr/bin/env python3
"""Deterministic local manuscript count; never a contest eligibility certificate."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def count(text):
    headings = list(re.finditer(r'^#{1,6}\s+(?:Bibliography|References)\s*#*\s*$', text, re.M | re.I))
    if len(headings) > 1:
        raise ValueError('multiple bibliography headings; explicit boundary review required')
    body = text[:headings[0].start()] if headings else text
    tokens = body.split()
    words = sum(bool(re.search(r'\w', token)) for token in tokens)
    return {'protocol': 'manuscript-count.v1', 'sha256': hashlib.sha256(text.encode()).hexdigest(),
            'whitespace_units': len(tokens), 'word_units': words,
            'bibliography_heading_found': bool(headings),
            'boundary': 'Before the sole Bibliography/References Markdown heading; title, headings, notes included. Word units are whitespace tokens with a Unicode letter, digit or underscore. Hyphenated words stay one unit.',
            'length_status': 'REQUIRES_SHORTENING' if words > 6000 else 'WITHIN_LOCAL_COUNT',
            'official_eligibility': 'NOT_CERTIFIED'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('file', type=Path)
    args = p.parse_args()
    print(json.dumps(count(args.file.read_text()), ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
