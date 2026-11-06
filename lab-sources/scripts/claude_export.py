"""Exact-byte export review. Detect common leaks, require human/AI reviewer attestation.
Never rewrites originals and never claims that regexes establish anonymity.
"""
import re
from research_archive import ArchiveError, canonical, sha

PROTOCOL = 'claude-export-review.v1'


def findings(path, data, policy):
    # Binary documents still need explicit content AND metadata review.
    text = path + '\n' + data.decode('utf-8', errors='replace')
    result = []
    for term in policy.get('private_terms', []):
        if not isinstance(term, str) or not term.strip():
            raise ArchiveError('invalid private term')
        if re.search(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text, re.I):
            result.append({'rule': 'private_term', 'match_digest': sha(term.casefold().encode()), 'blocking': True})
    for rule, regex, blocking in (
        ('local_path', r'(?:/Users/|/home/|[A-Za-z]:\\Users\\)[^\s"<>]+', True),
        ('email', r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', False),
        ('credential', r'(?i)(?:sk-[A-Za-z0-9_-]{16,}|Bearer\s+[A-Za-z0-9._-]{16,})', True),
    ):
        for match in re.findall(regex, text):
            result.append({'rule': rule, 'match_digest': sha(match.encode()), 'blocking': blocking})
    return sorted({canonical(x): x for x in result}.values(), key=lambda x: (x['rule'], x['match_digest']))


def candidate(files, policy):
    return {'protocol': PROTOCOL, 'policy_sha256': sha(canonical(policy)),
            'reviewer': '', 'reviewed_at': '', 'status': 'PENDING',
            'boundary': 'Selected exported bytes only; runtime paths/account context not anonymized.',
            'files': [{'path': p, 'sha256': sha(b), 'bytes': len(b),
                       'classification': 'UNREVIEWED', 'content_and_metadata_reviewed': False,
                       'personal_context_absent': False, 'notes': '',
                       'findings': findings(p, b, policy)} for p, b in sorted(files.items())]}


def verify(files, policy, review):
    expected = candidate(files, policy)
    if not isinstance(review, dict) or set(review) != set(expected):
        raise ArchiveError('export review schema differs')
    if (review['protocol'] != PROTOCOL or review['policy_sha256'] != expected['policy_sha256']
            or review['status'] != 'REVIEWED' or not isinstance(review['reviewer'], str)
            or not review['reviewer'].strip() or not isinstance(review['reviewed_at'], str)
            or not review['reviewed_at'].strip() or review['boundary'] != expected['boundary']):
        raise ArchiveError('export review missing or bound to another policy')
    if not isinstance(review['files'], list) or len(review['files']) != len(expected['files']):
        raise ArchiveError('review must cover every exported file')
    for actual, want in zip(review['files'], expected['files']):
        if not isinstance(actual, dict) or set(actual) != set(want):
            raise ArchiveError('export file review schema differs')
        for field in ('path', 'sha256', 'bytes', 'findings'):
            if actual[field] != want[field]:
                raise ArchiveError('export bytes or findings changed; review again')
        if (actual['content_and_metadata_reviewed'] is not True or actual['personal_context_absent'] is not True
                or actual['classification'] not in ('neutral_instruction', 'public_source', 'essay_artifact', 'technical_metadata')
                or not isinstance(actual['notes'], str) or not actual['notes'].strip()):
            raise ArchiveError('unreviewed content or metadata in export')
        if any(f['blocking'] for f in want['findings']):
            raise ArchiveError('private context detected; make a separate sanitized export')
    return sha(canonical(review))
