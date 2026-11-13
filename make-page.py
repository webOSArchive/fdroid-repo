#!/usr/bin/env python3
"""Writes the repository's web page: repo/index.html from web/index.html, and its QR code.

    python3 -I make-page.py      (add-apks.sh runs it after every fdroid update)

The page wears the webOS Archive's site template (web.css, and the shared menu taken fresh
from www.webosarchive.org/menu.php, without its analytics; web/menu-fallback.html if that
can't be reached). fdroid update leaves an index.html alone once it lacks fdroid's own
"auto-generated" comment, so this one stays. The app list is read from index-v2.json by the
page itself, so it never goes stale.
"""
import os
import re
import subprocess
import urllib.request

import qrcode
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))


def fingerprint(config):
    """The SHA-256 of the repository's signing certificate, as F-Droid shows it."""
    env = dict(os.environ, FDROID_KS_PASS=config['keystorepass'])
    out = subprocess.run(['keytool', '-list', '-v', '-keystore', os.path.join(HERE, config['keystore']),
                          '-alias', config['repo_keyalias'], '-storepass:env', 'FDROID_KS_PASS'],
                         capture_output=True, text=True, env=env, check=True).stdout
    return re.search(r'SHA256: ([0-9A-F:]+)', out).group(1).replace(':', '')


def menu():
    try:
        req = urllib.request.Request('https://www.webosarchive.org/menu.php',
                                     headers={'User-Agent': 'fdroid-repo-make-page'})
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode('utf-8')
        if 'menu-wrapper' not in html:
            raise ValueError('not the menu')
    except (OSError, ValueError) as e:
        print(f'make-page: the menu from www.webosarchive.org failed ({e}); using web/menu-fallback.html')
        with open(os.path.join(HERE, 'web', 'menu-fallback.html')) as f:
            return f.read()
    return re.sub(r'<!-- Matomo -->.*?<!-- End Matomo -->\s*', '', html, flags=re.S).strip()


def main():
    with open(os.path.join(HERE, 'config.yml')) as f:
        config = yaml.safe_load(f)
    address = config['repo_url'].rstrip('/')
    fp = fingerprint(config)
    with open(os.path.join(HERE, 'web', 'index.html')) as f:
        page = f.read()
    for key, value in {
        '@@MENU@@': menu(),
        '@@ADDRESS@@': address,
        '@@ADDRESS_NOSCHEME@@': re.sub(r'^https?://', '', address),
        '@@FINGERPRINT@@': fp,
        '@@FINGERPRINT_SPACED@@': ' '.join(fp[i:i + 2] for i in range(0, len(fp), 2)),
    }.items():
        page = page.replace(key, value)
    assert '@@' not in page, 'a placeholder in web/index.html was left unfilled'
    with open(os.path.join(HERE, 'repo', 'index.html'), 'w') as f:
        f.write(page)
    # The same link F-Droid's own page encodes: the client adds the repository from it.
    qrcode.make(f'{address}?fingerprint={fp}', border=2).save(os.path.join(HERE, 'repo', 'index.png'))
    print('make-page: repo/index.html and repo/index.png')


if __name__ == '__main__':
    main()
