"""Conservative high-confidence credential exclusion, never a secrecy proof."""
import re
import json

PATTERNS = tuple(re.compile(p) for p in (
    r'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?(?:-----END (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----|\Z)',
    r'\bsk-[A-Za-z0-9_-]{20,}\b',
    r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b',
    r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b',
    r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    r'(?i)\b(?:authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/-]{20,}',
    r'(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)["\x27]?\s*[:=]\s*["\x27][A-Za-z0-9_./+~=-]{20,}["\x27]',
))
SENSITIVE_KEYS={'api_key','apikey','api-key','client_secret','client-secret','access_token','access-token','password','private_key'}


def sensitive_pair(key,value):
    return (str(key).lower() in SENSITIVE_KEYS and isinstance(value,str) and len(value)>=8
            and value.lower() not in {'redacted','unknown','placeholder','your_api_key','your_password'})


def redact(text):
    result=text
    for pattern in PATTERNS: result=pattern.sub('[CREDENTIAL EXCLUDED]',result)
    return result, result!=text


def has_credential(text):
    return any(pattern.search(text) for pattern in PATTERNS)


def contains_credential(value,depth=0):
    if isinstance(value,dict): return any(sensitive_pair(k,v) or contains_credential(v,depth) for k,v in value.items())
    if isinstance(value,list): return any(contains_credential(v,depth) for v in value)
    if not isinstance(value,str): return False
    if has_credential(value): return True
    if depth<3 and value.lstrip().startswith(('{','[','"')):
        try: decoded=json.loads(value)
        except (ValueError,RecursionError): return False
        return contains_credential(decoded,depth+1)
    return False


def redact_value(value):
    if isinstance(value,dict): return {k:'[CREDENTIAL EXCLUDED]' if sensitive_pair(k,v) else redact_value(v) for k,v in value.items()}
    if isinstance(value,list): return [redact_value(v) for v in value]
    if isinstance(value,str):
        result,changed=redact(value)
        return result if changed or not contains_credential(value) else '[CREDENTIAL-BEARING VALUE EXCLUDED]'
    return value
