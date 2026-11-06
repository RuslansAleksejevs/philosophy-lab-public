"""Search published text, including conversations inside tar/gzip and ZIP files.

Standard library only. Builds a disposable SQLite index in .cache; never runs
archived programs, extracts archive paths, contacts providers or changes evidence.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import re
import sqlite3
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'archive-search-1'
SKIP_DIRS = {'.git', '.cache', '__pycache__', '.private'}
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.jsonl', '.py', '.tex', '.csv', '.tsv',
                 '.toml', '.yaml', '.yml', '.cff', '.html', '.xml', '.diff', '.source'}


def source_files(root):
    files = [p for p in root.rglob('*') if p.is_file() and not p.is_symlink()
                  and not (set(p.relative_to(root).parts) & SKIP_DIRS)
                  and p.suffix not in {'.pyc', '.tmp'}]
    def priority(p):
        name = p.relative_to(root).as_posix()
        group = 0 if name.startswith(('docs/', 'essays/', 'lab-sources/')) or name == 'README.md' else 1
        return (name.endswith(('.gz', '.zip')), group, name)
    return sorted(files, key=priority)


def fingerprint(root, files):
    h = hashlib.sha256(VERSION.encode())
    for p in files:
        stat = p.stat()
        h.update(f'{p.relative_to(root)}\0{stat.st_size}\0{stat.st_mtime_ns}\n'.encode())
    return h.hexdigest()


def text_members(root, files):
    """Yield locator and bytes; member names are display labels, never paths."""
    def unpack(raw, name, depth=0):
        if depth > 4:
            raise ValueError('Unexpected archive nesting: ' + name)
        if name.endswith('.tar.gz'):
            with tarfile.open(fileobj=io.BytesIO(raw), mode='r|gz') as archive:
                for member in archive:
                    if member.isfile():
                        yield from unpack(archive.extractfile(member).read(),
                                          name + '::' + member.name, depth + 1)
        elif name.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                for member in archive.infolist():
                    if not member.is_dir():
                        yield from unpack(archive.read(member), name + '::' + member.filename,
                                          depth + 1)
        elif name.endswith('.gz'):
            yield from unpack(gzip.decompress(raw), name[:-3], depth + 1)
        elif Path(name).suffix.lower() in TEXT_SUFFIXES or Path(name).name == 'Makefile':
            yield name, raw

    for p in files:
        yield from unpack(p.read_bytes(), p.relative_to(root).as_posix())


def essay_map(root):
    mapping = {}
    manifest = root / 'lab-sources/MANIFEST.json'
    if manifest.exists():
        for row in json.loads(manifest.read_text())['files']:
            mapping[row['path']] = ' '.join(row['essays'])
    for p in (root / 'essays').glob('E*/README.md'):
        for sid in re.findall(r'(?<![\w-])[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',
                              p.read_text()):
            previous = mapping.get(sid, '').split()
            mapping[sid] = ' '.join(sorted(set(previous + [p.parent.name])))
    return mapping


def documents(root, files):
    mapping, seen, seen_messages = essay_map(root), set(), set()
    for locator, raw in text_members(root, files):
        digest = hashlib.sha256(raw).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        try:
            body = raw.decode('utf-8')
        except UnicodeError:
            continue
        if '\0' in body:
            continue
        ids = set(re.findall(r'\b(?:E\d{3}|F\d{2}|S\d{2})\b', locator))
        ids.update(mapping.get(locator, '').split())
        try:
            doc = json.loads(body)
        except ValueError:
            doc = None
        if isinstance(doc, dict) and isinstance(doc.get('messages'), list):
            session = doc.get('session', {})
            sid = session.get('session_id') or doc.get('session_id') or ''
            ids.update(mapping.get(sid, '').split())
            for i, message in enumerate(doc['messages']):
                text = message.get('text')
                if not isinstance(text, str):
                    continue
                line = message.get('source_line', i + 1)
                identity = (sid, line, message.get('role'), text)
                if identity in seen_messages:
                    continue
                seen_messages.add(identity)
                title = f"{session.get('title') or sid} · {message.get('role', '')} · source line {line}"
                yield (locator + f'#source-line-{line}', title, text, 'conversation',
                       ' '.join(sorted(ids)), message.get('source_timestamp') or message.get('timestamp') or '')
        else:
            kind = ('essay' if locator.startswith('essays/') and
                    (locator.endswith('original.md') or '/final-20261101/' in locator or
                     '/selection-20261018/' in locator) else
                    'source' if locator.startswith('lab-sources/') else
                    'guide' if locator.startswith('docs/') or locator == 'README.md' else 'record')
            heading = re.search(r'^#{1,3}\s+(.+)', body, re.MULTILINE)
            title = heading.group(1) if heading else locator.split('::')[-1]
            yield (locator, title, body, kind, ' '.join(sorted(ids)), '')


def build_index(root, database, rebuild=False):
    files = source_files(root)
    signature = fingerprint(root, files)
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)')
    previous = connection.execute("SELECT value FROM metadata WHERE key='fingerprint'").fetchone()
    if previous and previous[0] == signature and not rebuild:
        return connection, False
    # A failed rebuild rolls back to the previous complete index.
    with connection:
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('DROP TABLE IF EXISTS archive')
        connection.execute("CREATE VIRTUAL TABLE archive USING fts5(title, body, locator UNINDEXED, kind UNINDEXED, essays, stamp UNINDEXED, tokenize='unicode61')")
        count = 0
        for locator, title, body, kind, essays, stamp in documents(root, files):
            connection.execute('INSERT INTO archive VALUES (?, ?, ?, ?, ?, ?)',
                               (title, body, locator, kind, essays, stamp))
            count += 1
        connection.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', ('fingerprint', signature))
        connection.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', ('documents', str(count)))
    return connection, True


def search(connection, query, kind=None, essay=None, limit=10, phrase=False, full=False):
    words = re.findall(r'[^\W_]+', query, re.UNICODE)
    if not words:
        raise ValueError('Enter at least one word or number.')
    match = '"' + ' '.join(words) + '"' if phrase else ' AND '.join('"' + w + '"' for w in words)
    clauses, values = ['archive MATCH ?'], [match]
    if kind:
        clauses.append('kind = ?'); values.append(kind)
    if essay:
        clauses.append("(' ' || essays || ' ') LIKE ?"); values.append('% ' + essay.upper() + ' %')
    values.append(limit)
    excerpt = 'body' if full else "snippet(archive, 1, '[', ']', ' … ', 28)"
    sql = ("SELECT title, locator, kind, essays, stamp, " + excerpt + ' '
           "FROM archive WHERE " + ' AND '.join(clauses) + ' ORDER BY rank LIMIT ?')
    keys = ['title', 'location', 'kind', 'essays', 'timestamp', 'excerpt']
    return [dict(zip(keys, row)) for row in connection.execute(sql, values)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?')
    parser.add_argument('--kind', choices=['essay', 'guide', 'source', 'conversation', 'record'])
    parser.add_argument('--essay', help='Filter by a recorded essay association, e.g. E012')
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--phrase', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--full', action='store_true', help='Print the complete matching text or message')
    parser.add_argument('--rebuild', action='store_true')
    parser.add_argument('--index-only', action='store_true')
    args = parser.parse_args()
    if not args.query and not args.index_only:
        parser.error('Supply a query or --index-only.')
    if not 1 <= args.limit <= 100:
        parser.error('--limit must be between 1 and 100.')
    try:
        db, rebuilt = build_index(ROOT, ROOT / '.cache/archive-search.sqlite3', args.rebuild)
        if args.index_only:
            print(json.dumps({'documents': int(db.execute("SELECT value FROM metadata WHERE key='documents'").fetchone()[0]), 'rebuilt': rebuilt}))
        else:
            results = search(db, args.query, args.kind, args.essay, args.limit, args.phrase, args.full)
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                for row in results:
                    print(row['title'] + '\n' + row['location'] + '\n' + row['excerpt'] + '\n')
                if not results:
                    print('No matching published text. Try fewer words or remove the essay filter.')
        db.close()
    except (ValueError, sqlite3.Error, OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        print('Search failed: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
