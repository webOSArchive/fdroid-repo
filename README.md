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

- `metadata/<application id>.yml`: each app's name, summary, description, licence and links,
  in F-Droid's metadata format. An app needs one before its APKs can be added.
- `add-apks.sh <apk>...`: copies APKs into `repo/` under names of their own
  (`<id>_<versionCode>[_arm32|_arm64].apk`) and re-signs the index. With no arguments it
  only re-signs, after a change to `metadata/`.
- `icons/repo-icon.png`: the repository's icon (Lunacy's, for now: see Lunacy's Meta/NOTICE).

Not in git: `config.yml` (the repository's settings and its keystore's passwords),
`keystore.p12` (its signing key), and `repo/` and `archive/`, which `fdroid update` writes.
`repo/` holds the only copy of every APK published, so keep it with the backups too.

## Publishing

1. `./add-apks.sh path/to/app-release.apk ...` (Lunacy: `Meta/fdroid/update-repo.sh` in its
   own repository, after `./build.sh publish`).
2. Upload **only** `repo/` and `archive/` to `feeds/fdroid/` on stacks.webosarchive.org, by
   hand. Never the folder itself: `keystore.p12` and `config.yml` are the signing key and its
   passwords, and anything else here is of no use to the client.

Once an app has more than `archive_older` (3) versions, the oldest move to `archive/`.

## Adding an app

1. Write `metadata/<application id>.yml`: `Categories`, `License`, `AuthorName`, `WebSite`,
   `SourceCode`, `IssueTracker`, `Changelog`, `Name`, `Summary` (80 characters at most) and
   `Description`. Copy one of Lunacy's.
2. `./add-apks.sh` its release APKs. An app with one APK per ABI gives them the same version
   code; the client picks the one the device runs.

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
