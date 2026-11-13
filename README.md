# webOS Archive F-Droid repository

An F-Droid repository for Android apps from the webOS community, hosted by the webOS Archive
beside its Preware feeds. If you've made an Android app for webOS fans (a port, a companion,
a tool), you can publish it here, and people get your updates through the F-Droid client.

**Repository address:** `https://stacks.webosarchive.org/feeds/fdroid/repo`

You keep building, signing and releasing your app the way you do now. The repository takes
your release APKs straight from your GitHub releases, checks them, and lists them. Nothing
is rebuilt, re-signed or changed, so people who installed your app from GitHub get updates
from here and the other way round.

## Adding your app

Open a pull request that adds two files, both named after your app's application id
(`com.example.myapp`).

### 1. `metadata/<application id>.yml`: what people see

```yaml
Categories:
  - System
License: Apache-2.0
AuthorName: Your Name
WebSite: https://github.com/you/myapp
SourceCode: https://github.com/you/myapp
IssueTracker: https://github.com/you/myapp/issues
Changelog: https://github.com/you/myapp/releases
AllowedAPKSigningKeys: <your signing certificate's SHA-256>

Name: My App
Summary: One line, 80 characters at most
Description: |-
    What your app does, in plain text: a paragraph or two. A blank line starts a new
    paragraph, and lines starting with "* " make a list.
```

- **Categories** are one or more of F-Droid's usual ones, such as `Games`, `Internet`,
  `Multimedia`, `Phone & SMS`, `System`, `Theming` or `Writing`.
- **License** is an SPDX identifier (`Apache-2.0`, `GPL-3.0-or-later`, `MIT`...).
- **AllowedAPKSigningKeys** is the SHA-256 of the certificate you sign releases with. Get it
  from any release APK with the Android SDK's `apksigner`:

  ```sh
  apksigner verify --print-certs myapp-release.apk | grep SHA-256
  ```

  Use the 64 hex characters after "SHA-256 digest:". APKs signed with any other key are
  refused, so if your release page is ever tampered with, nobody can put another app in
  your app's place.

[Lunacy's metadata](metadata/org.webosarchive.lunacy.yml) is a complete example.

### 2. `sources/<application id>.yml`: where your releases are

```yaml
GitHub: you/myapp
Assets:
  - myapp-release.apk
```

- **GitHub** is the repository whose releases hold your APKs.
- **Assets** are the file names to take from each release. `*` works as a wildcard. If you
  ship one APK per ABI, list each one, and give them all the same version code; F-Droid
  installs the one that fits the device.
  ([Lunacy's](sources/org.webosarchive.lunacy.yml) does this.)
- The newest release that isn't a draft is used, pre-releases included. Add
  `Prereleases: false` to skip them.

### Before you open the pull request

- Your APKs are **release builds**, signed with the same key every time.
- Each release has a **higher version code** than the last.
- Your newest GitHub release has the APKs attached under the names in `sources/`.
- The application id is yours, and isn't already listed here.

Once your pull request is merged, your app appears at the next update of the repository.

## Releasing updates

Publish a new GitHub release with the APKs attached and a higher version code. That's all:
the repository picks it up at its next update. You don't need another pull request unless
you change your description, your asset names or your signing key.

To change your signing key, send a pull request adding the new key to
`AllowedAPKSigningKeys` (as a list, both keys during the changeover). Bear in mind that
Android itself won't update an installed app with one signed by a different key, so your
users would have to uninstall first.

## Using the repository

In the F-Droid client: **Settings → Repositories → +**, and enter
`https://stacks.webosarchive.org/feeds/fdroid/repo`. Or open that address in a browser on
your phone for a link and QR code. The repository's fingerprint (SHA-256) is:

    E441B611BFE19109A873451865AEE9871800E9EF8677F725CD3F31C1182FC96E

## Maintaining the repository

Publishing, the signing key and the tools: see [MAINTAINING.md](MAINTAINING.md).
