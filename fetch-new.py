#!/usr/bin/env python3
"""Fetches each app's newest release from GitHub and adds what is new to the repository.

    python3 -I fetch-new.py            every app in sources/
    python3 -I fetch-new.py <app id>   just that one

For each sources/<app id>.yml, this takes the newest GitHub release that isn't a draft (a
pre-release counts unless the file says otherwise), and every asset named in its Assets. An
asset already in repo/ or archive/ (by SHA-256) is skipped. A new one is downloaded, checked
against the SHA-256 GitHub reports for it, checked to be that app, and checked to be signed by
a key the app's metadata allows (AllowedAPKSigningKeys). Only then does add-apks.sh add it and
re-sign the index. Nothing is added if any check fails.

Set GITHUB_TOKEN to raise GitHub's limit of 60 unauthenticated requests an hour.
"""
import fnmatch
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SDK = os.environ.get('ANDROID_HOME', os.path.expanduser('~/Android/Sdk'))


def tool(name):
    # apksigner from build-tools 34: later versions' verify can disagree with older clients.
    found = sorted(glob.glob(os.path.join(SDK, 'build-tools', '*', name)))
    if not found:
        sys.exit(f'fetch-new: no {name} in {SDK}/build-tools')
    return found[0] if name == 'apksigner' else found[-1]


def get(url, accept='application/vnd.github+json'):
    req = urllib.request.Request(url, headers={'Accept': accept, 'User-Agent': 'fdroid-repo-fetch-new'})
    if os.environ.get('GITHUB_TOKEN'):
        req.add_header('Authorization', 'Bearer ' + os.environ['GITHUB_TOKEN'])
    return urllib.request.urlopen(req, timeout=60)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def published():
    """The SHA-256 of every APK the repository already has."""
    return {sha256(p) for d in ('repo', 'archive') for p in glob.glob(os.path.join(HERE, d, '*.apk'))}


def signers(apk):
    out = subprocess.run([tool('apksigner'), 'verify', '--print-certs', apk],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise ValueError('its signature does not verify: ' + out.stderr.strip()[:200])
    return set(re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([0-9a-f]{64})$', out.stdout, re.M))


def package(apk):
    out = subprocess.run([tool('aapt2'), 'dump', 'badging', apk], capture_output=True, text=True)
    m = re.match(r"package: name='([^']+)'", out.stdout)
    if not m:
        raise ValueError('aapt2 cannot read it')
    return m.group(1)


def fetch(app_id, have, workdir):
    """Downloads and checks this app's new assets; returns their paths, or raises ValueError."""
    with open(os.path.join(HERE, 'sources', app_id + '.yml')) as f:
        source = yaml.safe_load(f)
    meta_path = os.path.join(HERE, 'metadata', app_id + '.yml')
    if not os.path.isfile(meta_path):
        raise ValueError(f'no metadata/{app_id}.yml')
    with open(meta_path) as f:
        allowed = yaml.safe_load(f).get('AllowedAPKSigningKeys') or []
    # One key may be written on the line itself, as F-Droid's metadata allows.
    allowed = {str(k).lower() for k in ([allowed] if isinstance(allowed, str) else allowed)}
    if not allowed:
        raise ValueError(f'metadata/{app_id}.yml has no AllowedAPKSigningKeys')
    repo, patterns = source['GitHub'], source['Assets']
    prereleases = source.get('Prereleases', True)

    with get(f'https://api.github.com/repos/{repo}/releases?per_page=20') as r:
        releases = json.load(r)
    release = next((r for r in releases if not r['draft'] and (prereleases or not r['prerelease'])), None)
    if release is None:
        raise ValueError(f'{repo} has no release to take')
    assets = [a for a in release['assets'] if any(fnmatch.fnmatchcase(a['name'], p) for p in patterns)]
    if not assets:
        raise ValueError(f"{repo} {release['tag_name']} has no asset matching {patterns}")

    new = []
    for a in assets:
        digest = (a.get('digest') or '').removeprefix('sha256:')
        if digest and digest in have:
            continue
        dest = os.path.join(workdir, f"{app_id}-{a['id']}.apk")
        print(f"{app_id}: downloading {a['name']} from {repo} {release['tag_name']}")
        with get(a['browser_download_url'], accept='application/octet-stream') as r, open(dest, 'wb') as f:
            while block := r.read(1 << 20):
                f.write(block)
        got = sha256(dest)
        if digest and got != digest:
            raise ValueError(f"{a['name']}: SHA-256 {got} is not GitHub's {digest}")
        if got in have:
            continue
        if package(dest) != app_id:
            raise ValueError(f"{a['name']} is {package(dest)}, not {app_id}")
        keys = signers(dest)
        if not keys or not keys <= allowed:
            raise ValueError(f"{a['name']} is signed by {sorted(keys)}, which metadata/{app_id}.yml doesn't allow")
        new.append(dest)
    return new


def main():
    ids = sys.argv[1:] or sorted(os.path.splitext(n)[0] for n in os.listdir(os.path.join(HERE, 'sources'))
                                 if n.endswith('.yml'))
    have = published()
    with tempfile.TemporaryDirectory(prefix='fetch-new-') as workdir:
        to_add, failed = [], []
        for app_id in ids:
            try:
                apks = fetch(app_id, have, workdir)
            except (ValueError, OSError, KeyError) as e:
                print(f'{app_id}: SKIPPED, {e}', file=sys.stderr)
                failed.append(app_id)
                continue
            print(f'{app_id}: {len(apks)} new' if apks else f'{app_id}: up to date')
            to_add += apks
        if to_add:
            subprocess.run([os.path.join(HERE, 'add-apks.sh')] + to_add, check=True)
        else:
            print('Nothing new to add.')
    if failed:
        sys.exit(f"fetch-new: {', '.join(failed)} skipped (above)")


if __name__ == '__main__':
    main()
