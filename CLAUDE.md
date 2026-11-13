# webOS Archive F-Droid repository: notes for agents

Read [README.md](README.md) (how apps are added, for contributors) and
[MAINTAINING.md](MAINTAINING.md) (publishing, the signing key, the tools, setting up on a new
machine) first. The maintainer is **codepoet** ([codepoet80](https://github.com/codepoet80)).

## Rules

1. **Upload only `repo/` and `archive/`** to `feeds/fdroid/` on stacks.webosarchive.org. The
   rest of this folder, above all `keystore.p12` and `config.yml`, never leaves this machine
   except as a private backup. When telling codepoet what to upload, name exactly those two
   folders and where they go.
2. **The secrets never go in git.** `.gitignore` keeps them out; check `git status` before a
   commit. Never print `config.yml`'s passwords.
3. **fdroidserver comes only from the pinned venv** in MAINTAINING.md (`--no-deps`, exact
   versions). An unpinned `pip install fdroidserver` has run for an hour and taken the machine
   down. Run `fdroid update` only through `add-apks.sh`, which caps it.
4. **Never rebuild, re-sign or change an app's APK.** The repository publishes developers'
   own release builds; `AllowedAPKSigningKeys` in each app's metadata is the check, and is
   never loosened to let an APK through.
5. **Don't run `fdroid update` on a `repo/` missing older APKs** (a fresh clone): it drops them
   from the feed. MAINTAINING.md, "Setting up on another machine".
6. Ask before any outward-facing action: pushes, PRs, anything sent to the server.

Commits go on `main`.
