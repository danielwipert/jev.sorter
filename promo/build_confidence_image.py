"""Render the LinkedIn image for post 2: promo/confidence-60.html -> promo/confidence-60.png.

Needs Node + Playwright (same setup as build_carousel.py).
Fonts load from Google Fonts; pass a folder with Fontsource files to render offline:
  python promo/build_confidence_image.py [path/to/fonts]
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

RENDER_JS = r"""
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
(async () => {
  const [html, png, fonts] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + html, { waitUntil: 'load' });
  if (fonts) {
    const f = (fam, file, w, s) => `@font-face{font-family:"${fam}";font-weight:${w};font-style:${s};src:url(file://${fonts}/${file})}`;
    await p.addStyleTag({ content: [
      f('Newsreader', 'fontsource-newsreader/files/newsreader-latin-500-normal.woff2', 500, 'normal'),
      f('Inter', 'fontsource-inter/files/inter-latin-400-normal.woff2', 400, 'normal'),
      f('Inter', 'fontsource-inter/files/inter-latin-600-normal.woff2', 600, 'normal'),
    ].join('\n') });
  }
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await (await p.$('.slide')).screenshot({ path: png });
  console.log('Wrote ' + png);
  await b.close();
})();
"""


def main():
    script = HERE / "_render.js"
    script.write_text(RENDER_JS)
    try:
        subprocess.run(["node", str(script), str(HERE / "confidence-60.html"), str(HERE / "confidence-60.png"),
                        sys.argv[1] if len(sys.argv) > 1 else ""], check=True)
    finally:
        script.unlink()


if __name__ == "__main__":
    main()
