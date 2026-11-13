# The webOS Archive's F-Droid repository

An F-Droid repository for the webOS Archive's Android apps, hosted beside its Preware feeds:
**https://stacks.webosarchive.org/feeds/fdroid/repo**. Users add that address in the F-Droid
client (or open `repo/index.html` there for a link and QR code) and get each app's releases
from it. The address has to end in `/repo`: fdroidserver refuses anything else, and finds
the archive beside it at `/archive`.

Each app here is its developer's own release build, signed with the app's usual key, so a
copy installed from GitHub or elsewhere updates from here and the other way round. Nothing
is built from source here, and F-Droid's own inclusion rules don't apply.

## What is here

- `metadata/<application id>.yml`: each app's name, summary, description, licence, links and
  the signing keys its APKs may carry (`AllowedAPKSigningKeys`), in F-Droid's metadata format.
- `sources/<application id>.yml`: where its releases are, for `fetch-new.py`.
- `fetch-new.py`: takes each app's newest GitHub release, checks it, and adds what is new.
- `add-apks.sh <apk>...`: adds APKs on hand (copied into `repo/` as
  `<id>_<versionCode>[_arm32|_arm64].apk`) and re-signs the index. With no arguments it only
  re-signs, after a change to `metadata/`.
- `icons/repo-icon.png`: the repository's icon (Lunacy's, for now: see Lunacy's Meta/NOTICE).

Not in git: `config.yml` (the repository's settings and its keystore's passwords),
`keystore.p12` (its signing key), and `repo/` and `archive/`, which `fdroid update` writes.
The APKs live in `repo/`, never in git: a few releases of Lunacy alone would outgrow it.

## Adding your app

Send a pull request with two files. Your APKs stay on your own GitHub releases; the
repository's maintainer fetches them from there.

1. `metadata/<your application id>.yml`, after Lunacy's:

   ```yaml
   Categories:
     - System
   License: Apache-2.0
   AuthorName: Your Name
   WebSite: https://github.com/you/yourapp
   SourceCode: https://github.com/you/yourapp
   IssueTracker: https://github.com/you/yourapp/issues
   Changelog: https://github.com/you/yourapp/releases
   AllowedAPKSigningKeys: <your signing certificate's SHA-256>

   Name: Your App
   Summary: One line, 80 characters at most
   Description: |-
       What it does, in plain text. A paragraph or two.
   ```

   `AllowedAPKSigningKeys` is your release key's certificate digest, from
   `apksigner verify --print-certs your-app-release.apk` ("Signer #1 certificate SHA-256
   digest"). An APK signed by any other key is refused, so a release page that was tampered
   with can't put another app in your app's place.
2. `sources/<your application id>.yml`:

   ```yaml
   GitHub: you/yourapp
   Assets:
     - yourapp-release.apk
   ```

   `Assets` are the names (or `*` patterns) of the release assets to take: one APK, or one per
   ABI with the same version code. The newest release that isn't a draft is taken; add
   `Prereleases: false` to skip pre-releases.

Each later release is picked up the next time the maintainer runs `fetch-new.py`: publish it
on GitHub with the next version code, and that's all. The APKs must be release builds, signed
the same way each time, with a version code that goes up.

## Publishing

1. `python3 -I fetch-new.py`: every app's new releases, checked and added. (Or
   `./add-apks.sh <apk>...` for APKs on hand; Lunacy's `Meta/fdroid/update-repo.sh` does this
   with a fresh build before its release is on GitHub.)
2. Upload **only** `repo/` and `archive/` to `feeds/fdroid/` on stacks.webosarchive.org, by
   hand. The rest of this folder stays here.

Once an app has more than `archive_older` (3) versions, the oldest move to `archive/`.

## The signing key

**Back up `keystore.p12` and `config.yml`.** The key is the repository's identity: losing it
means every user has to remove the repository and add it again. Its fingerprint (SHA-256),
which users can check when they add the repository:

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
