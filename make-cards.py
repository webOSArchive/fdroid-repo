#!/usr/bin/env python3
"""Draws the pages' link-preview cards (web/card-repo.png, web/card-archive.png), 1200x630 as
Twitter's large cards and Facebook want. Run it again only to change them; the PNGs are
committed and make-page.py copies them into place.

    python3 -I make-cards.py [Lunacy checkout]     (default ~/Projects/Lunacy)

The type is webOS's own Prelude, from Lunacy's assets (Palm/HP's, distributed as abandonware:
see the NOTICE beside the fonts there); the robot is Lunacy's icon (icons/repo-icon.png).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/Projects/Lunacy'),
                     'AndroidLuna', 'src', 'main', 'assets', 'luna', 'fonts')
W, H = 1200, 630
BLUE, INK, GREY = (25, 118, 210), (34, 34, 34), (120, 120, 120)

CARDS = {
    'repo': ('F-Droid Repository', 'Android apps from the webOS community,', 'with updates through F-Droid.'),
    'archive': ('F-Droid Archive', 'Older versions of the apps in the', 'webOS Archive F-Droid repository.'),
}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def fitted(name, size, text, width):
    """The font at the largest size up to `size` at which `text` fits in `width`."""
    while size > 12 and font(name, size).getlength(text) > width:
        size -= 1
    return font(name, size)


def main():
    icon = Image.open(os.path.join(HERE, 'icons', 'repo-icon.png')).convert('RGBA')
    icon.thumbnail((330, 380), Image.LANCZOS)
    for key, (title, line1, line2) in CARDS.items():
        card = Image.new('RGB', (W, H), 'white')
        draw = ImageDraw.Draw(card)
        draw.rectangle([0, H - 18, W, H], fill=BLUE)
        card.paste(icon, (80, (H - 18 - icon.height) // 2), icon)
        x = 80 + icon.width + 60
        room = W - x - 70
        draw.text((x, 150), 'webOS Archive', font=fitted('Prelude-Medium.ttf', 44, 'webOS Archive', room), fill=GREY)
        draw.text((x, 205), title, font=fitted('Prelude-Bold.ttf', 72, title, room), fill=INK)
        body = fitted('Prelude-Medium.ttf', 36, max(line1, line2, key=len), room)
        draw.text((x, 320), line1, font=body, fill=INK)
        draw.text((x, 320 + int(body.size * 1.3)), line2, font=body, fill=INK)
        url = 'stacks.webosarchive.org/feeds/fdroid'
        draw.text((x, 470), url, font=fitted('Prelude-Medium.ttf', 30, url, room), fill=BLUE)
        out = os.path.join(HERE, 'web', f'card-{key}.png')
        card.save(out, optimize=True)
        print(f'make-cards: {out}')


if __name__ == '__main__':
    main()
