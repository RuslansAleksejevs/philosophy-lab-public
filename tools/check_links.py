"""Check local destinations and anchors in the edition's editorial navigation.

Original manuscripts and verbatim conversations are evidence, not link fixtures.
Their text is never rewritten to make this check pass. Standard library only.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import html
import json
import re


ROOT = Path(__file__).resolve().parents[1]
INLINE_LINK = re.compile(r'!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)')
REFERENCE_LINK = re.compile(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)', re.MULTILINE)


def anchors(path):
    text = path.read_text(encoding='utf-8')
    found = set(re.findall(r'<(?:a|h[1-6])\b[^>]*\bid=["\']([^"\']+)', text))
    counts = {}
    fence = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(('```', '~~~')):
            token = stripped[:3]
            fence = None if fence == token else token if fence is None else fence
            continue
        if fence:
            continue
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$', line)
        if not match:
            continue
        title = re.sub(r'<[^>]*>', '', match[1])
        title = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', title)
        title = html.unescape(title).lower()
        slug = re.sub(r'[^\w\s-]', '', title).replace(' ', '-')
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        found.add(slug + (f'-{n}' if n else ''))
    return found


def editorial_files(root):
    files = set(root.rglob('README.md'))
    files.update((root / 'docs').glob('*.md'))
    files.update([root / 'ROADMAP.md', root / 'PUBLICATION.md', root / 'logs/DATES.md'])
    return sorted(p for p in files if '.git' not in p.parts)


def check_links(root=ROOT):
    root = Path(root).resolve()
    errors, count, anchor_count, cache = [], 0, 0, {}
    files = editorial_files(root)
    for path in files:
        text = path.read_text(encoding='utf-8')
        # Ignore code examples, which are not rendered navigation.
        text = re.sub(r'(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$', '', text)
        destinations = [m.group(1) for m in INLINE_LINK.finditer(text)]
        destinations.extend(m.group(1) for m in REFERENCE_LINK.finditer(text))
        for destination in destinations:
            destination = html.unescape(destination.strip('<>'))
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue
            count += 1
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            error = None
            if not target.is_relative_to(root):
                error = 'destination leaves repository'
            elif not target.exists():
                error = 'missing destination'
            elif parsed.fragment and target.is_file() and target.suffix.lower() == '.md':
                anchor_count += 1
                if target not in cache:
                    cache[target] = anchors(target)
                if unquote(parsed.fragment) not in cache[target]:
                    error = 'missing anchor'
            if error:
                errors.append({'file': str(path.relative_to(root)), 'destination': destination, 'error': error})
    return {'status': 'FAIL' if errors else 'PASS', 'editorial_files': len(files),
            'local_links': count, 'anchors_checked': anchor_count, 'errors': errors,
            'scope': 'Editorial navigation; remote URLs and verbatim research/conversation bodies are not checked.'}


if __name__ == '__main__':
    result = check_links()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
