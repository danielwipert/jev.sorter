"""Render the LinkedIn carousel: promo/carousel.html -> promo/jev-vs-the-frontier.pdf (+ PNG previews).

Numbers come from docs/data.json (run build_site_data.py first). Needs Node + Playwright.
Fonts load from Google Fonts; pass a folder with Fontsource files to render offline:
  python promo/build_carousel.py [path/to/fonts]
"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

RENDER_JS = r"""
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
(async () => {
  const [html, pdf, pngPrefix, fonts] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + html, { waitUntil: 'load' });
  if (fonts) {
    const f = (fam, file, w, s) => `@font-face{font-family:"${fam}";font-weight:${w};font-style:${s};src:url(file://${fonts}/${file})}`;
    await p.addStyleTag({ content: [
      f('Newsreader', 'fontsource-newsreader/files/newsreader-latin-400-normal.woff2', 400, 'normal'),
      f('Newsreader', 'fontsource-newsreader/files/newsreader-latin-500-normal.woff2', 500, 'normal'),
      f('Newsreader', 'fontsource-newsreader/files/newsreader-latin-400-italic.woff2', 400, 'italic'),
      f('Inter', 'fontsource-inter/files/inter-latin-400-normal.woff2', 400, 'normal'),
      f('Inter', 'fontsource-inter/files/inter-latin-600-normal.woff2', 600, 'normal'),
      f('Inter', 'fontsource-inter/files/inter-latin-700-normal.woff2', 700, 'normal'),
    ].join('\n') });
  }
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.pdf({ path: pdf, width: '1080px', height: '1350px', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  const slides = await p.$$('.slide');
  for (let i = 0; i < slides.length; i++) await slides[i].screenshot({ path: `${pngPrefix}${i + 1}.png` });
  console.log(`Wrote ${pdf} (${slides.length} slides)`);
  await b.close();
})();
"""


def main():
    data = json.loads((HERE.parent / "docs" / "data.json").read_text())
    (HERE / "carousel-data.js").write_text("window.CAROUSEL_DATA = " + json.dumps(data) + ";\n")
    script = HERE / "_render.js"
    script.write_text(RENDER_JS)
    fonts = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        subprocess.run(["node", str(script), str(HERE / "carousel.html"), str(HERE / "jev-vs-the-frontier.pdf"),
                        str(HERE / "preview-slide-"), fonts], check=True)
    finally:
        script.unlink()


if __name__ == "__main__":
    main()
