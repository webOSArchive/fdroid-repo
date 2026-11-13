# Maintaining the repository

For whoever holds the repository's signing key. Contributors don't need any of this; see
[README.md](README.md).

## What is here

- `metadata/<application id>.yml` and `sources/<application id>.yml`: each app's listing
  and where its releases are (README.md).
- `fetch-new.py`: takes each app's newest GitHub release, checks it, and adds what is new.
- `add-apks.sh <apk>...`: adds APKs on hand (copied into `repo/` as
  `<id>_<versionCode>[_arm32|_arm64].apk`) and re-signs the index. With no arguments it only
  re-signs, after a change to `metadata/`.
- `metadata/<application id>/en-US/icon.png`: an app's icon. Apps with adaptive launcher
  icons need one, since fdroid update can't take a PNG icon from their APKs.
- `make-page.py` and `web/`: the repository's web page (`repo/index.html`, and the QR code
  `repo/index.png`), in the webOS Archive's site template, with the shared menu taken fresh from
  www.webosarchive.org (its analytics left out; `web/menu-fallback.html` if it can't be
  reached). add-apks.sh runs it after every update. fdroid update leaves a page alone once it
  lacks fdroid's "auto-generated" comment, so this one stays. The app list is read from
  `index-v2.json` by the page itself. Each page's link preview (Open Graph and Twitter tags)
  shows `web/card-repo.png` or `web/card-archive.png`, copied to `preview/card.png`; they are
  drawn by `make-cards.py` in webOS's Prelude font, and committed, so run it only to change them.
- `icons/repo-icon.png`: the repository's icon (Lunacy's, for now: see Lunacy's Meta/NOTICE).

Not in git: `config.yml` (the repository's settings and its keystore's passwords),
`keystore.p12` (its signing key), and `repo/` and `archive/`, which `fdroid update` writes.
The APKs live in `repo/`, never in git: a few releases of Lunacy alone would outgrow it.

## Reviewing a pull request

- The application id is the app's real one and isn't taken.
- `AllowedAPKSigningKeys` matches the certificate on the app's current GitHub release
  (`apksigner verify --print-certs`), and the GitHub repository is the developer's own.
- The description is accurate, and the app is a fit for the repository.

After merging, run `fetch-new.py` for the new app (below) and check its listing.

## Publishing

1. `python3 -I fetch-new.py` (or `python3 -I fetch-new.py <application id>` for one app).
   For each app it takes the newest release, skips what is already published (by SHA-256),
   and checks each new APK's checksum against GitHub's, its application id, and its signing
   key against `AllowedAPKSigningKeys`. An app that fails a check is skipped with the reason;
   the rest are added and the index re-signed. Set `GITHUB_TOKEN` if GitHub's limit of 60
   requests an hour gets in the way.

   For APKs on hand, `./add-apks.sh <apk>...` instead. Lunacy's `Meta/fdroid/update-repo.sh`
   does this with a fresh build, before its release is on GitHub.
2. Upload **only** `repo/` and `archive/` to `feeds/fdroid/` on stacks.webosarchive.org, by
   hand. The rest of this folder stays here.

Once an app has more than `archive_older` (3) versions, the oldest move to `archive/`, which
the client shows only when a user asks for older versions.

The address has to end in `/repo`: fdroidserver refuses any other, and finds the archive
beside it at `/archive`.

## The signing key

**Back up `keystore.p12` and `config.yml`.** The key is the repository's identity: losing it
means every user has to remove the repository and add it again. It signs the index, which
lists every APK's SHA-256, so the client can tell the repository's real index from a forged
one; the apps themselves stay signed by their developers. Its fingerprint (SHA-256):

    E441B611BFE19109A873451865AEE9871800E9EF8677F725CD3F31C1182FC96E

It was made on 2026-11-13 with keytool (PKCS12, RSA 4096, alias `webosarchive`); config.yml
has `repo_url`, `repo_name` ("webOS Archive"), `repo_description`, `repo_icon: icon.png`
(which add-apks.sh copies from icons/) and `archive_older: 3`.

## fdroidserver

fdroidserver 2.4.5 with androguard 4.1.4, in a virtualenv at `~/.local/share/fdroidserver`
that also sees the system's packages. Ubuntu's own fdroidserver (2.2.1, with androguard 3.4)
can't read APKs from AGP 8 ("res1 must be zero!"), but is installed for its dependencies.
pip's resolver can run for a very long time on fdroidserver's dependencies, so the venv takes
exact versions with no dependency resolution:

    sudo apt install fdroidserver python3.12-venv
    python3 -m venv --system-site-packages ~/.local/share/fdroidserver
    P=~/.local/share/fdroidserver/bin/pip
    $P install --no-deps --only-binary :all: androguard==4.1.4
    $P install --no-deps fdroidserver==2.4.5 apkInspector loguru mutf8 platformdirs \
        puremagic python-vagrant sdkmanager dataset

add-apks.sh runs `fdroid update` under a 6 GB memory cap and a 15-minute timeout; it takes a
few seconds.
