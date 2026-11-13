#!/bin/sh
# Adds release APKs to the repository and re-signs its index.
#
#   ./add-apks.sh <apk>...     add these, then update the index
#   ./add-apks.sh              just update the index (after editing metadata/)
#
# Each APK is copied into repo/ as <application id>_<versionCode>[_<abi>].apk, so a release
# never replaces an earlier one; one with the same name and different bytes is refused, since
# a version code is published once. Every app needs metadata/<application id>.yml first.
# Afterwards, upload repo/ and archive/ (MAINTAINING.md).
set -eu
cd "$(dirname "$0")"
FDROID=${FDROID:-$HOME/.local/share/fdroidserver/bin/fdroid}
SDK=${ANDROID_HOME:-$HOME/Android/Sdk}
AAPT2=$(ls -d "$SDK"/build-tools/*/aapt2 | sort -V | tail -1)

die() { echo "add-apks: $*" >&2; exit 1; }
[ -f config.yml ] && [ -f keystore.p12 ] || die "config.yml or keystore.p12 is missing (MAINTAINING.md)"
[ -x "$FDROID" ] || die "no fdroid at $FDROID (MAINTAINING.md)"

for apk; do
    [ -f "$apk" ] || die "$apk: no such file"
    badge=$("$AAPT2" dump badging "$apk") || die "$apk: not an APK"
    id=$(echo "$badge" | sed -n "s/^package: name='\([^']*\)'.*/\1/p")
    code=$(echo "$badge" | sed -n "s/^package: .* versionCode='\([^']*\)'.*/\1/p")
    [ -f "metadata/$id.yml" ] || die "$apk: no metadata/$id.yml for $id"
    # An APK with one ABI is named after it, so an app's per-ABI APKs can share a version code.
    abi=$(echo "$badge" | sed -n "s/^native-code: '\([^']*\)'$/\1/p")
    case $abi in armeabi-v7a) abi=_arm32 ;; arm64-v8a) abi=_arm64 ;; '') ;; *) abi=_$abi ;; esac
    dest="repo/${id}_${code}${abi}.apk"
    if [ -f "$dest" ]; then cmp -s "$apk" "$dest" || die "$dest exists and differs; a version code is published once"
    else mkdir -p repo && cp "$apk" "$dest" && echo "added $(basename "$dest")"; fi
done

cp icons/repo-icon.png icon.png
# Capped and niced, so a runaway can't take the machine with it; fdroid update itself takes
# seconds and well under a gigabyte.
ANDROID_HOME=$SDK systemd-run --user --scope -q -p MemoryMax=6G timeout 900 nice "$FDROID" update
echo "Ready to upload: only repo/ and archive/ (the rest stays here) to https://stacks.webosarchive.org/feeds/fdroid/"
