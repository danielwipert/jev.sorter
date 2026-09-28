"""Draw the calibration chart ("does 90 mean 90?") for the results page.

Reads results/calibration.csv (written by analyze.py) and writes docs/calibration.svg.
Plain SVG, no plotting library. Hover a point to see its numbers.
"""

from pathlib import Path

import pandas as pd

SERIES = [  # contender, label, color (categorical slots 1-3, validated as a set)
    ("B", "Jev (v2)", "#2a78d6"),
    ("C", "Sonnet 5", "#eb6834"),
    ("D", "Haiku 4.5", "#1baf7a"),
]
BAND_MIDPOINTS = {"0-49": 25, "50-59": 55, "60-69": 65, "70-79": 75, "80-89": 85, "90-100": 95}
SMALL_N = 20  # points from fewer messages than this are drawn hollow

SURFACE, INK, INK_2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
W, H = 720, 440
LEFT, RIGHT, TOP, BOTTOM = 56, 24, 104, 56
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"


def x_of(band_index, dodge=0):
    step = (W - LEFT - RIGHT) / len(BAND_MIDPOINTS)
    return LEFT + step * (band_index + 0.5) + dodge


def y_of(percent):
    return TOP + (H - TOP - BOTTOM) * (1 - percent / 100)


def main():
    data = pd.read_csv("results/calibration.csv")
    bands = list(BAND_MIDPOINTS)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
        f'aria-labelledby="t d" style="font-family:{FONT};background:{SURFACE}">',
        '<title id="t">Calibration: accuracy within each confidence band, test set</title>',
        '<desc id="d">For each model, the share of answers that were correct, grouped by the confidence the '
        'model reported. The gray line is perfect calibration. Hollow points rest on fewer than 20 messages.</desc>',
        f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
        f'<text x="{LEFT}" y="24" font-size="15" font-weight="600" fill="{INK}">Does a confidence of 90 mean 90% right?</text>',
        f'<text x="{LEFT}" y="44" font-size="12" fill="{INK_2}">Share of answers correct, by the confidence each model '
        f'reported. Test set, 1,000 messages per model.</text>',
        f'<text x="{LEFT}" y="61" font-size="12" fill="{INK_2}">Hollow point = fewer than {SMALL_N} messages '
        f'in that band. Hover a point for its numbers.</text>',
    ]

    # Legend (always present for 2+ series): line-key + dot, text in ink.
    lx = LEFT
    for _, label, color in SERIES:
        out.append(f'<line x1="{lx}" y1="86" x2="{lx + 18}" y2="86" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        out.append(f'<circle cx="{lx + 9}" cy="86" r="4" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
        out.append(f'<text x="{lx + 24}" y="90" font-size="12" fill="{INK}">{label}</text>')
        lx += 24 + 8 * len(label) + 24
    out.append(f'<line x1="{lx}" y1="86" x2="{lx + 18}" y2="86" stroke="{MUTED}" stroke-width="1"/>')
    out.append(f'<text x="{lx + 24}" y="90" font-size="12" fill="{INK_2}">Perfect calibration</text>')

    # Gridlines and y ticks (hairline, solid, recessive).
    for tick in (0, 25, 50, 75, 100):
        y = y_of(tick)
        out.append(f'<line x1="{LEFT}" y1="{y}" x2="{W - RIGHT}" y2="{y}" stroke="{AXIS if tick == 0 else GRID}" stroke-width="1"/>')
        out.append(f'<text x="{LEFT - 8}" y="{y + 4}" font-size="11" fill="{MUTED}" text-anchor="end" '
                   f'style="font-variant-numeric:tabular-nums">{tick}%</text>')
    for i, band in enumerate(bands):
        out.append(f'<text x="{x_of(i)}" y="{H - BOTTOM + 20}" font-size="11" fill="{MUTED}" text-anchor="middle">{band.replace("-", "–")}</text>')
    out.append(f'<text x="{(LEFT + W - RIGHT) / 2}" y="{H - 12}" font-size="12" fill="{INK_2}" text-anchor="middle">Confidence the model reported</text>')

    # Perfect-calibration reference: accuracy equals the band's midpoint.
    ref = " ".join(f"{x_of(i):.1f},{y_of(BAND_MIDPOINTS[b]):.1f}" for i, b in enumerate(bands))
    out.append(f'<polyline points="{ref}" fill="none" stroke="{MUTED}" stroke-width="1"/>')

    # Series: 2px lines broken where a band has no answers, dodged sideways so points don't overlap.
    for s, (key, label, color) in enumerate(SERIES):
        dodge = (s - 1) * 8
        rows = data[data["contender"] == key].set_index("confidence_band")
        points = []
        for i, band in enumerate(bands):
            n = int(rows.loc[band, "messages"])
            accuracy = None if n == 0 else float(str(rows.loc[band, "accuracy"]).rstrip("%"))
            points.append((i, band, n, accuracy))
        run = []
        # Lines only join points resting on enough messages; small ones stand alone, hollow.
        for i, band, n, accuracy in points + [(None, None, 0, None)]:
            if accuracy is None or n < SMALL_N:
                if len(run) > 1:
                    out.append(f'<polyline points="{" ".join(run)}" fill="none" stroke="{color}" stroke-width="2" '
                               f'stroke-linejoin="round" stroke-linecap="round"/>')
                run = []
            else:
                run.append(f"{x_of(i, dodge):.1f},{y_of(accuracy):.1f}")
        for i, band, n, accuracy in points:
            if accuracy is None:
                continue
            cx, cy = x_of(i, dodge), y_of(accuracy)
            tip = f"{label} · confidence {band.replace('-', '–')} · {accuracy:.1f}% right ({n} messages)"
            if n < SMALL_N:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{SURFACE}" stroke="{color}" stroke-width="2"/>')
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
            # Hit target bigger than the mark; native tooltip on hover.
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="transparent"><title>{tip}</title></circle>')

    out.append("</svg>")
    Path("docs").mkdir(exist_ok=True)
    Path("docs/calibration.svg").write_text("\n".join(out) + "\n")
    print("Wrote docs/calibration.svg")


if __name__ == "__main__":
    main()
