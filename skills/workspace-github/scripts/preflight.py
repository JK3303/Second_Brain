"""Read-only, stdlib-only Git candidate inspection. No authentication or mutation."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess


def git(root, *args, absent_ok=False):
    env = os.environ.copy()
    env['GIT_OPTIONAL_LOCKS'] = '0'
    result = subprocess.run(['git', '-C', str(root), '--literal-pathspecs', *args],
                            capture_output=True, env=env)
    if result.returncode and not (absent_ok and result.returncode == 1):
        raise ValueError('Git inspection failed; diagnose ownership/access without exposing raw errors')
    return result.stdout


def selected_file(root, value, allow_deleted=False):
    portable = value.replace('\\', '/')
    path = PurePosixPath(portable)
    if (not portable or path.is_absolute() or PureWindowsPath(value).drive or
            '..' in path.parts or not path.parts or path.as_posix() != portable or
            '.git' in path.parts):
        raise ValueError('Selected paths must be canonical repository-relative files')
    target = root.joinpath(*path.parts)
    resolved = target.resolve()
    if not resolved.is_relative_to(root) or target.is_symlink():
        raise ValueError('Selected file escapes the repository or is a symlink')
    if resolved.is_file():
        return path.as_posix(), False
    if target.exists():
        raise ValueError('Selected path is not a file')
    name = path.as_posix()
    if allow_deleted:
        in_index = git(root, 'ls-files', '--stage', '-z', '--', name)
        in_head = git(root, 'ls-tree', '-z', 'HEAD', '--', name)
        if in_index or in_head:
            return name, True
    raise ValueError('Selected file is missing or escapes the repository')


def relative_file(root, value):
    """Compatibility entry point for a required existing file."""
    return selected_file(root, value)[0]


def status_paths(root):
    fields = git(root, 'status', '--porcelain=v1', '-z', '--untracked-files=all').decode('utf-8', 'surrogateescape').split('\0')
    changed, staged = set(), set()
    index = 0
    while index < len(fields) and fields[index]:
        entry = fields[index]
        names = {entry[3:]}
        if 'R' in entry[:2] or 'C' in entry[:2]:
            index += 1
            if index < len(fields) and fields[index]:
                names.add(fields[index])
        changed.update(names)
        if entry[0] not in (' ', '?'):
            staged.update(names)
        index += 1
    return changed, staged


def changed_paths(root):
    return status_paths(root)[0]


def inspect(repo, candidates=(), inputs=()):
    root = Path(repo).resolve()
    actual = Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if root != actual:
        raise ValueError('--repo must be the exact Git repository root')
    selections = dict(selected_file(root, p, allow_deleted=True) for p in candidates)
    candidate = set(selections)
    selected = candidate | {relative_file(root, p) for p in inputs}
    changed, staged = status_paths(root)
    blocked = sorted((changed & selected) - candidate)
    hashes = {p: None if selections.get(p, False) else git(root, 'hash-object', '--', p).decode().strip()
              for p in sorted(selected)}
    groups = {}
    for p in changed:
        top = p.split('/', 1)[0] if '/' in p else '[root files]'
        groups[top] = groups.get(top, 0) + 1
    fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    branch = git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD', absent_ok=True).decode().strip() or None
    index_hash = hashlib.sha256(git(root, 'ls-files', '--stage', '-z')).hexdigest()
    context = {'root': str(root), 'head': head, 'branch': branch, 'index_entries_sha256': index_hash}
    context_fingerprint = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()
    return {'root': str(root), 'head': head, 'branch': branch,
            'changed_count': len(changed), 'groups': dict(sorted(groups.items())[:20]),
            'groups_truncated': len(groups) > 20, 'candidate': sorted(candidate),
            'deleted_candidates': sorted(p for p, deleted in selections.items() if deleted),
            'input_hashes': hashes, 'fingerprint': fingerprint,
            'context_fingerprint': context_fingerprint,
            'staged_count': len(staged), 'staged_candidate': sorted(staged & candidate),
            'unrelated_staged_count': len(staged - candidate), 'blocked_inputs': blocked,
            'status': 'blocked' if blocked else 'eligible', 'validation_passed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--candidate', action='append', default=[])
    parser.add_argument('--input', action='append', default=[])
    args = parser.parse_args()
    try:
        report = inspect(args.repo, args.candidate, args.input)
    except (ValueError, OSError):
        print(json.dumps({'status': 'blocked', 'error': 'Root/path/Git inspection failed; verify exact repository and selected files'}))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 2 if report['status'] == 'blocked' else 0


if __name__ == '__main__':
    raise SystemExit(main())
