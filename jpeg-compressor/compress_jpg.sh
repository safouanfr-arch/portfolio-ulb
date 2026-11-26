#!/usr/bin/env bash
set -uo pipefail

usage() {
    printf '%s\n' \
        "Usage: $0 [-c|--strip] [-r|--recursive] [-e|--ext EXT] PIXELS PATH" \
        "Writes BASE.compressed.EXT beside each JPEG. Default EXT: jpg."
}

fail() {
    printf 'Error: %s\n' "$*" >&2
    exit 2
}

strip=0
recursive=0
extension=jpg

while (( $# > 0 )); do
    case $1 in
        -h|--help) usage; exit 0 ;;
        -c|--strip) strip=1; shift ;;
        -r|--recursive) recursive=1; shift ;;
        -e|--ext)
            (( $# >= 2 )) || fail "$1 needs an extension"
            extension=$2
            shift 2
            ;;
        --) shift; break ;;
        -*) fail "unknown option: $1" ;;
        *) break ;;
    esac
done

(( $# == 2 )) || { usage >&2; exit 2; }
resolution=$1
source_path=$2
[[ -n $source_path ]] || fail "PATH must not be empty"
[[ $resolution =~ ^[1-9][0-9]*$ ]] || fail "PIXELS must be a positive integer"

shopt -s nocasematch
case $extension in
    jpg|jpeg|jpe|jif|jfif|jfi) ;;
    *) fail "expected a JPEG extension such as jpg or jpeg" ;;
esac
shopt -u nocasematch

[[ $source_path = /* ]] || source_path=$PWD/$source_path
[[ -d $source_path || -f $source_path ]] || fail "path does not exist: $source_path"

if command -v magick >/dev/null 2>&1; then
    image_tool=magick
elif command -v convert >/dev/null 2>&1 && convert -version 2>/dev/null | grep -qi ImageMagick; then
    image_tool=convert
else
    fail "ImageMagick is required (magick or convert)"
fi

compress_file() (
    local source=$1
    local destination="${1%.*}.compressed.$extension"
    local temporary
    if [[ -e $destination || -L $destination ]]; then
        printf 'Skipped: %s already exists\n' "$destination" >&2
        return 0
    fi

    temporary=$(mktemp "${source%/*}/.compress-jpg.XXXXXXXX") || return 1
    trap 'rm -f -- "$temporary"' EXIT
    trap 'exit 1' HUP INT TERM

    local flags=(-auto-orient -resize "${resolution}x${resolution}>")
    if (( strip )); then
        flags+=(-strip)
    fi
    flags+=(-quality 85 -interlace Plane -sampling-factor 4:2:0)

    if ! "$image_tool" "jpeg:$source" "${flags[@]}" "jpeg:$temporary"; then
        printf 'Failed to compress: %s\n' "$source" >&2
        return 1
    fi
    # Hard-linking publishes the completed file without overwriting an existing path.
    if ! ln -T -- "$temporary" "$destination"; then
        printf 'Failed to create: %s\n' "$destination" >&2
        return 1
    fi
    printf 'Wrote %s\n' "$destination"
)

compress_list() {
    local source status=0
    while IFS= read -r -d '' source; do
        compress_file "$source" || status=1
    done
    return "$status"
}

if [[ -d $source_path ]]; then
    depth=()
    if (( ! recursive )); then
        depth=(-maxdepth 1)
    fi
    find -H "$source_path" "${depth[@]}" -type f \
        \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.jpe' -o -iname '*.jif' -o -iname '*.jfif' -o -iname '*.jfi' \) \
        ! -iname '*.compressed.*' -print0 | compress_list
else
    shopt -s nocasematch
    [[ $source_path =~ \.(jpg|jpeg|jpe|jif|jfif|jfi)$ ]] || fail "expected a JPEG file"
    shopt -u nocasematch
    compress_file "$source_path"
fi
