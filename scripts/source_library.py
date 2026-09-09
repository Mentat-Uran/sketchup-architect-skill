#!/usr/bin/env python3
"""Offline source retrieval. No network, app control, or source-tree writes."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

SKILL = Path(__file__).resolve().parents[1]
CONFIG = json.loads((SKILL / 'references/source-config.json').read_text())
FORMAT = '2'
GROUPS = {
    'api': ['github/ruby-api-docs-gh-pages'],
    'legacy': ['github/ruby-api-docs'],
    'stubs': ['github/ruby-api-stubs/lib/sketchup-api-stubs/stubs'],
    'guides': ['developer-guides'],
    'desktop': ['desktop-help'],
    'tutorials': ['github/sketchup-ruby-api-tutorials', 'github/sketchup-ruby-api-tutorials-wiki',
                  'github/sketchup-shapes', 'github/sketchup-stl', 'github/htmldialog-examples',
                  'github/sketchup-extension-vscode-project', 'github/testup-2', 'github/rubocop-sketchup'],
    'release': ['github/ruby-api-stubs/pages/ReleaseNotes.md', 'metadata/github-releases'],
    'reference': ['github/ruby-api-stubs/pages', 'github/ruby-api-stubs/README.md'],
    'quick': ['quick-reference'],
    'issues': ['github-issues/api-issue-tracker/issues-all.json'],
}


class PlainHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.parts = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript', 'svg'):
            self.skip += 1
        if not self.skip and tag in ('p', 'div', 'br', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'pre'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'svg'):
            self.skip = max(0, self.skip - 1)
        if not self.skip and tag in ('p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'pre'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_path(root, relative):
    root = root.resolve()
    p = (root / relative).resolve()
    if not p.is_relative_to(root):
        raise ValueError('Source path must remain within the configured library')
    if not p.is_file():
        raise FileNotFoundError(str(p))
    return p


def extract(path):
    if path.suffix.lower() == '.pdf':
        if shutil.which('pdftotext'):
            return subprocess.run(['pdftotext', '-layout', str(path), '-'], check=True,
                                  text=True, capture_output=True).stdout
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError('PDF extraction needs pdftotext or pypdf. Use Python from load_workspace_dependencies.') from exc
        return '\n'.join('PAGE %d\n%s' % (i + 1, p.extract_text())
                         for i, p in enumerate(PdfReader(path).pages))
    raw = path.read_text(encoding='utf-8', errors='replace')
    if path.suffix.lower() in ('.html', '.htm'):
        parser = PlainHTML()
        parser.feed(raw)
        return '\n'.join(line for line in
                         (re.sub(r'[\t \r]+', ' ', x).strip() for x in ''.join(parser.parts).splitlines()) if line)
    return raw


def manifest(root):
    return json.loads(source_path(root, 'metadata/SOURCE_MANIFEST.json').read_text())


def files(root):
    seen = set()
    for category, locations in GROUPS.items():
        for location in locations:
            base = root / location
            candidates = [base] if base.is_file() else sorted(base.rglob('*'))
            for p in candidates:
                if not p.is_file() or any(x.startswith('.') or x == 'raw' for x in p.relative_to(root).parts):
                    continue
                if p.suffix.lower() not in ('.html', '.md', '.rb', '.pdf', '.json'):
                    continue
                rel = p.relative_to(root).as_posix()
                if rel in seen:
                    continue
                seen.add(rel)
                yield ('release' if category != 'legacy' and 'releasenotes' in p.name.lower() else category), rel, p


def urls(root):
    out = {}
    p = root / 'metadata/web-pages.jsonl'
    if p.exists():
        for line in p.read_text().splitlines():
            r = json.loads(line)
            out[r['local_html']] = r.get('canonical_url', '')
    for r in manifest(root)['sources']:
        if (root / r['local_path']).is_file():
            out.setdefault(r['local_path'], r.get('source_location', ''))
    return out


def url_for(rel, mapping):
    if rel in mapping:
        return mapping[rel]
    if rel.startswith('github/ruby-api-docs-gh-pages/'):
        return 'https://ruby.sketchup.com/' + rel.split('/', 2)[2]
    if rel.startswith('github/'):
        _, repo, remainder = rel.split('/', 2)
        if repo.endswith('-wiki'):
            return 'https://github.com/SketchUp/' + repo[:-5] + '/wiki/' + Path(remainder).stem
        return 'https://github.com/SketchUp/' + repo + '/blob/main/' + remainder
    return ''


def blocks(text):
    start, current, size = 1, [], 0
    for i, line in enumerate(text.splitlines(), 1):
        if current and (len(current) >= 55 or size + len(line) > 7000):
            yield start, '\n'.join(current)
            start, current, size = i, [], 0
        current.append(line)
        size += len(line)
    if current:
        yield start, '\n'.join(current)


def build(root, db):
    mapping = urls(root)
    db.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='index-', suffix='.sqlite', dir=db.parent)
    os.close(fd)
    con = sqlite3.connect(temporary)
    counts, skipped, seen_hash = {}, [], set()
    try:
        con.executescript('CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);'
                          'CREATE TABLE sources(path TEXT PRIMARY KEY,sha256 TEXT);'
                          'CREATE VIRTUAL TABLE chunks USING fts5(title,body,category UNINDEXED,path UNINDEXED,url UNINDEXED,line UNINDEXED,sha256 UNINDEXED);')
        for category, rel, p in files(root):
            sha = digest(p)
            con.execute('INSERT INTO sources VALUES(?,?)', (rel, sha))
            if sha in seen_hash:
                continue
            seen_hash.add(sha)
            if category == 'issues':
                for issue in json.loads(p.read_text()):
                    title = '#%s %s [%s]' % (issue['number'], issue['title'], issue['state'])
                    for line, chunk in blocks(str(issue.get('body') or '(no body)')):
                        con.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?)',
                                    (title, chunk, category, rel + '#' + str(issue['number']),
                                     issue['html_url'], line, sha))
                    counts[category] = counts.get(category, 0) + 1
                continue
            try:
                body = extract(p)
            except RuntimeError as exc:
                skipped.append({'path': rel, 'reason': str(exc)})
                continue
            for line, chunk in blocks(body):
                con.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?)',
                            (rel, chunk, category, rel, url_for(rel, mapping), line, sha))
            counts[category] = counts.get(category, 0) + 1
        metadata = {'format': FORMAT, 'root': str(root), 'snapshot': manifest(root).get('generated_at'),
                    'manifest_sha256': digest(root / 'metadata/SOURCE_MANIFEST.json'),
                    'counts': counts, 'skipped': skipped}
        con.executemany('INSERT INTO meta VALUES(?,?)', [(k, json.dumps(v)) for k, v in metadata.items()])
        con.commit()
        con.close()
        os.replace(temporary, db)
        return metadata
    finally:
        con.close()
        if Path(temporary).exists():
            Path(temporary).unlink()


def connect(root, db):
    if not db.exists():
        raise RuntimeError('Index missing. Run the index command first.')
    con = sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    meta = {r['key']: json.loads(r['value']) for r in con.execute('SELECT * FROM meta')}
    if meta['root'] != str(root) or meta['format'] != FORMAT or meta['manifest_sha256'] != digest(root / 'metadata/SOURCE_MANIFEST.json'):
        con.close()
        raise RuntimeError('Index root/schema/manifest changed. Rebuild the index.')
    return con, meta


def search(root, db, query, category, limit):
    con, meta = connect(root, db)
    terms = re.findall(r'[\w]+', query)
    if not terms:
        raise ValueError('Provide a word or API symbol to search')
    expression = ' AND '.join('"' + t + '"' for t in terms)
    sql = 'SELECT *,snippet(chunks,1,"[", "]"," … ",36) AS excerpt FROM chunks WHERE chunks MATCH ?'
    params = [expression]
    if category:
        sql += ' AND category=?'
        params.append(category)
    else:
        sql += " AND category != 'legacy'"
    sql += ' ORDER BY bm25(chunks,5.0,1.0) LIMIT ?'
    params.append(limit)
    results, hashes = [], {}
    for row in con.execute(sql, params):
        r = dict(row)
        rel = r['path'].split('#')[0]
        if rel not in hashes:
            hashes[rel] = digest(source_path(root, rel))
        r['stale'] = hashes[rel] != r['sha256']
        r.pop('body')
        results.append(r)
    con.close()
    return {'snapshot': meta['snapshot'], 'results': results,
            'note': 'HTML/PDF use extracted-text lines; Ruby/Markdown use source lines. Read context before relying on a hit.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path)
    p.add_argument('--cache', type=Path)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('status').add_argument('--verify', action='store_true', help='Hash indexed files and detect added/removed sources')
    sub.add_parser('index')
    s = sub.add_parser('search')
    s.add_argument('query')
    s.add_argument('--category', choices=GROUPS)
    s.add_argument('--limit', type=int, default=6)
    r = sub.add_parser('read')
    r.add_argument('path', help='Relative source path; append #issue-number for an issue')
    r.add_argument('--start', type=int, default=1)
    r.add_argument('--lines', type=int, default=90)
    r.add_argument('--comments', action='store_true')
    args = p.parse_args()
    configured_root = args.root or os.environ.get('SKETCHUP_SOURCE_ROOT') or CONFIG.get('source_root')
    if not configured_root:
        raise RuntimeError('Configure the official SketchUp source library with --root or SKETCHUP_SOURCE_ROOT')
    root = Path(configured_root).expanduser().resolve()
    cache = (args.cache or (Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / CONFIG['cache_subdirectory'])).expanduser().resolve()
    db = cache / (hashlib.sha256(str(root).encode()).hexdigest()[:12] + '.sqlite')
    try:
        m = manifest(root)
        if args.command == 'index':
            result = build(root, db)
            result['cache'] = str(db)
        elif args.command == 'status':
            result = {'root': str(root), 'snapshot': m.get('generated_at'), 'cache': str(db),
                      'source_groups': {k: all((root / x).exists() for x in v) for k, v in GROUPS.items()},
                      'indexed': db.exists(), 'launches_sketchup': False}
            if db.exists():
                con, meta = connect(root, db)
                result['index'] = meta
                if args.verify:
                    indexed = {r['path']: r['sha256'] for r in con.execute('SELECT * FROM sources')}
                    now = {rel: digest(f) for _, rel, f in files(root)}
                    result['changed_paths'] = sorted(k for k in indexed.keys() | now.keys() if indexed.get(k) != now.get(k))
                con.close()
        elif args.command == 'search':
            if not 1 <= args.limit <= 30:
                raise ValueError('limit must be 1..30')
            result = search(root, db, args.query, args.category, args.limit)
        else:
            rel, _, issue_id = args.path.partition('#')
            source = source_path(root, rel)
            if issue_id:
                issue = next(x for x in json.loads(source.read_text()) if x['number'] == int(issue_id))
                body = json.dumps({k: issue.get(k) for k in ('number', 'title', 'state', 'state_reason', 'updated_at', 'html_url', 'labels', 'milestone', 'body')}, indent=2, ensure_ascii=False)
                if args.comments:
                    cp = root / 'github-issues/api-issue-tracker/comments' / (issue_id + '.json')
                    if cp.exists():
                        body += '\nCOMMENTS\n' + json.dumps([{k: c.get(k) for k in ('created_at', 'updated_at', 'html_url', 'body')} for c in json.loads(cp.read_text())], indent=2, ensure_ascii=False)
            else:
                body = extract(source)
            if args.start < 1 or not 1 <= args.lines <= 400:
                raise ValueError('start must be positive; lines must be 1..400')
            lines = body.splitlines()
            result = {'path': str(source), 'sha256': digest(source), 'total_lines': len(lines),
                      'line_basis': 'extracted text' if source.suffix in ('.html', '.pdf', '.json') else 'source',
                      'text': '\n'.join('%d: %s' % (i + 1, lines[i]) for i in range(args.start - 1, min(len(lines), args.start - 1 + args.lines)))}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.command == 'status' and (result.get('changed_paths') or not all(result['source_groups'].values())):
            return 2
        return 0
    except (OSError, ValueError, RuntimeError, sqlite3.Error, StopIteration) as exc:
        print(json.dumps({'error': str(exc) or 'Requested record not found'}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
