#!/usr/bin/env python3
"""Writes the web pages of the repository and its archive (repo/ and archive/index.html) from
web/index.html, with their QR codes.

    python3 -I make-page.py      (add-apks.sh runs it after every fdroid update)

The page wears the webOS Archive's site template (web.css, and the shared menu taken fresh
from www.webosarchive.org/menu.php, without its analytics; web/menu-fallback.html if that
can't be reached). fdroid update leaves an index.html alone once it lacks fdroid's own
"auto-generated" comment, so this one stays. The app list is read from index-v2.json by the
page itself, so it never goes stale.
"""
import os
import re
import shutil
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


REPO_LEAD = ('Android apps from the webOS community, among them '
             '<a href="https://www.webosarchive.org/lunacy/">Lunacy</a>, which runs webOS apps on '
             "Android. Add this repository to F-Droid and you'll get each app's updates as they're "
             'released.')
ARCHIVE_LEAD = ('Older versions of the apps in the <a href="../repo/">webOS Archive F-Droid '
                "repository</a>, for going back to one. You don't need this to get updates: add the "
                'repository itself, and turn on its archive in F-Droid only if you want older versions.')

PAGES = {
    'repo': {'@@TITLE@@': 'F-Droid Repository', '@@HEADING@@': 'webOS Archive F-Droid Repository',
             '@@LEAD@@': REPO_LEAD, '@@APPS_HEADING@@': 'Apps', '@@EMPTY@@': 'No apps yet.',
             '@@ALL_VERSIONS@@': 'false',
             '@@DESCRIPTION@@': 'Android apps from the webOS community, among them Lunacy, which runs '
                                "webOS apps on Android. Add it to F-Droid for each app's updates."},
    'archive': {'@@TITLE@@': 'F-Droid Archive', '@@HEADING@@': 'webOS Archive F-Droid Archive',
                '@@LEAD@@': ARCHIVE_LEAD, '@@APPS_HEADING@@': 'Older versions',
                '@@EMPTY@@': 'No older versions yet: every version is still in the repository.',
                '@@ALL_VERSIONS@@': 'true',
                '@@DESCRIPTION@@': 'Older versions of the apps in the webOS Archive F-Droid repository.'},
}


def main():
    with open(os.path.join(HERE, 'config.yml')) as f:
        config = yaml.safe_load(f)
    fp = fingerprint(config)
    the_menu = menu()
    with open(os.path.join(HERE, 'web', 'index.html')) as f:
        template = f.read()
    for folder, words in PAGES.items():
        # The archive is a repository of its own, beside the main one, signed by the same key.
        address = re.sub(r'/repo$', '/' + folder, config['repo_url'].rstrip('/'))
        page = template
        for key, value in dict(words, **{
            '@@MENU@@': the_menu,
            '@@ADDRESS@@': address,
            '@@ADDRESS_NOSCHEME@@': re.sub(r'^https?://', '', address),
            '@@FINGERPRINT@@': fp,
            '@@FINGERPRINT_SPACED@@': ' '.join(fp[i:i + 2] for i in range(0, len(fp), 2)),
        }).items():
            page = page.replace(key, value)
        assert '@@' not in page, 'a placeholder in web/index.html was left unfilled'
        os.makedirs(os.path.join(HERE, folder), exist_ok=True)
        with open(os.path.join(HERE, folder, 'index.html'), 'w') as f:
            f.write(page)
        # Its link-preview card (make-cards.py), at the address og:image names: in a folder of its
        # own, since fdroid update takes any file at the top of repo/ for a package.
        os.makedirs(os.path.join(HERE, folder, 'preview'), exist_ok=True)
        shutil.copyfile(os.path.join(HERE, 'web', f'card-{folder}.png'), os.path.join(HERE, folder, 'preview', 'card.png'))
        # The same link F-Droid's own page encodes: the client adds the repository from it.
        qrcode.make(f'{address}?fingerprint={fp}', border=2).save(os.path.join(HERE, folder, 'index.png'))
        print(f'make-page: {folder}/index.html and {folder}/index.png')


if __name__ == '__main__':
    main()
