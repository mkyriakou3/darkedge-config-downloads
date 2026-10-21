"""Publish a config folder of this repo to the DarkEdge config downloader.

The bot (DarkEdge ConfigDownloaderService) reads the manifest
"darkedge-config-downloader-manifest.json" from the gist below. Every entry points to a
folder of this repo; the bot downloads that folder into "configs/public/<folder>_DE".
Raising an entry's "version" makes users who already downloaded it see "update available".

Usage (from this repo's root, needs the GitHub CLI "gh" logged in with the "gist" scope):
    python publish_config.py <folder> [--group KEY ...] [--bump] [--no-push] [--dry-run]

    <folder>      folder in this repo to publish (e.g. krist-apotheosis)
    --group KEY   group key(s) shown in the bot's downloader table (new entries only,
                  or to replace the keys of an existing entry)
    --bump        existing entry: increase its version (default when the entry exists)
    --no-push     skip "git add/commit/push" of the folder (gist only)
    --dry-run     print the new manifest without changing anything
"""
import argparse
import json
import os
import subprocess
import sys

GIST_ID = '916772de5dfd2c09e965d72f1bb8c444'
MANIFEST_FILE = 'darkedge-config-downloader-manifest.json'
REPO_URL = 'https://github.com/mkyriakou3/darkedge-config-downloads/tree/main/'
REPO_DIR = os.path.dirname(os.path.abspath(__file__))


def run(args, **kw):
    print('>', ' '.join(args))
    return subprocess.run(args, check=True, cwd=REPO_DIR, **kw)


def fetch_manifest():
    out = subprocess.run(['gh', 'api', f'gists/{GIST_ID}'], check=True, capture_output=True, cwd=REPO_DIR)
    gist = json.loads(out.stdout.decode('utf-8'))
    return json.loads(gist['files'][MANIFEST_FILE]['content'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folder')
    ap.add_argument('--group', action='append', default=None)
    ap.add_argument('--bump', action='store_true')
    ap.add_argument('--no-push', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    folder = a.folder.strip('/\\')
    if not os.path.isdir(os.path.join(REPO_DIR, folder)):
        sys.exit(f'folder not found in repo: {folder}')
    if any(c in folder for c in ' /\\'):
        sys.exit('folder name must not contain spaces or slashes')

    manifest = fetch_manifest()
    configs = manifest.setdefault('configs', [])
    url = REPO_URL + folder
    entry = next((c for c in configs if c.get('downloadUrl', '').rstrip('/') == url), None)
    if entry is None:
        entry = {'downloadUrl': url, 'groupKeys': a.group or [], 'version': 1}
        configs.insert(0, entry)
        print(f'adding new entry {folder} (version 1)')
    else:
        entry['version'] = int(entry.get('version', 1)) + 1
        if a.group is not None:
            entry['groupKeys'] = a.group
        print(f'updating {folder} to version {entry["version"]}')

    new_content = json.dumps(manifest, indent=2, ensure_ascii=False) + '\n'
    if a.dry_run:
        print(new_content)
        return

    # 1) the folder must be on GitHub (main) before the manifest points to it
    if not a.no_push:
        run(['git', 'add', '--', folder])
        staged = subprocess.run(['git', 'diff', '--cached', '--quiet', '--', folder], cwd=REPO_DIR).returncode != 0
        if staged:
            run(['git', 'commit', '-m', f'Publish {folder} config (v{entry["version"]})', '--', folder])
        run(['git', 'push', 'origin', 'HEAD:main'])

    # 2) update the gist manifest
    body = os.path.join(REPO_DIR, '.gist-body.json')
    with open(body, 'w', encoding='utf-8') as f:
        json.dump({'files': {MANIFEST_FILE: {'content': new_content}}}, f, ensure_ascii=False)
    try:
        run(['gh', 'api', '-X', 'PATCH', f'gists/{GIST_ID}', '--input', body], stdout=subprocess.DEVNULL)
    finally:
        os.remove(body)
    print('done. The bot fetches the manifest with a cache-buster, but the gist raw CDN can take a few minutes.')


if __name__ == '__main__':
    main()
