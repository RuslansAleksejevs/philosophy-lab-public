#!/usr/bin/env python3
"""Read-only runtime check; no provider availability is inferred."""
import ast
import json
import os
from pathlib import Path
import sys
import fcntl

root = Path(__file__).resolve().parents[1]
errors = []
if sys.version_info < (3, 9):
    errors.append('Python 3.9+ required')
for option in ('O_NOFOLLOW', 'O_DIRECTORY'):
    if not hasattr(os, option):
        errors.append('runtime missing ' + option)
for path in sorted((root / 'scripts').glob('*.py')):
    try:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    except (OSError, SyntaxError) as exc:
        errors.append(str(exc))
print(json.dumps({'status': 'FAIL' if errors else 'PASS', 'errors': errors,
                  'python': sys.version.split()[0], 'archive': 'local stdlib filesystem',
                  'provider_capture': 'Must be checked per explicit session; not inferred from doctor',
                  'optional_provider': 'UNCONFIGURED'}, indent=2))
sys.exit(bool(errors))
