#!/usr/bin/env python3
"""Static plates, gis-cartography house style.

Plate I  - faithful recreation of the IEM map, rebuilt on verified data.
Plate II - the house-style map: 2026 reports as a multiple of each state's own
           2004-2025 average. Normalised, diverging, true midpoint at 1.0x.

Projection EPSG:5070 (NAD83 / Conus Albers) -- equal area, which is what
comparing a quantity between states requires.

Layout follows the NPS habit of working the marginal ocean: legend over the
Pacific, note over the Atlantic, small-state callouts stacked off the
northeast coast in latitude order so no leader line crosses another.
"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrow
from matplotlib.collections import PatchCollection

HERE = pathlib.Path(__file__).parent
B = HERE / "build"
F = json.loads((HERE / "findings.json").read_text())
G = json.loads((B / "states_albers.json").read_text())
S = F["states"]

SANS, SERIF = "Avenir Next", "Iowan Old Style"
INK, INK2, MUTED = "#1E1D1B", "#4A473F", "#7A756B"
PAPER, FRAME, WATER = "#FBFAF7", "#D9D5CC", "#DEE7ED"

XLIM = (-2460000, 3060000)
YLIM = (140000, 3310000)
CALLOUT = ["VT", "NH", "MA", "RI", "CT", "NJ", "DE", "MD"]
NUDGE = {"MI": (30000, 20000), "FL": (55000, 25000), "LA": (-45000, 40000),
         "VA": (75000, -15000), "CA": (0, -70000), "ID": (0, -170000),
         "MN": (0, -70000), "NY": (60000, -40000), "OK": (65000, 0),
         "WV": (-20000, -20000), "KY": (45000, 0), "TN": (30000, 0),
         "NE": (20000, 0), "MD": (60000, -20000)}


def centroids():
    c = {}
    for ab, s in G.items():
        best, ba = None, -1
        for ring in s["rings"]:
            a = abs(sum(ring[i][0]*ring[i+1][1] - ring[i+1][0]*ring[i][1]
                        for i in range(len(ring)-1)) / 2)
            if a > ba:
                ba, best = a, ring
        A = sum(best[i][0]*best[i+1][1] - best[i+1][0]*best[i][1]
                for i in range(len(best)-1)) / 2
        cx = sum((best[i][0]+best[i+1][0]) *
                 (best[i][0]*best[i+1][1]-best[i+1][0]*best[i][1])
                 for i in range(len(best)-1)) / (6*A)
        cy = sum((best[i][1]+best[i+1][1]) *
                 (best[i][0]*best[i+1][1]-best[i+1][0]*best[i][1])
                 for i in range(len(best)-1)) / (6*A)
        dx, dy = NUDGE.get(ab, (0, 0))
        c[ab] = (cx+dx, cy+dy)
    return c

CEN = centroids()


def classify(v, breaks):
    for i, b in enumerate(breaks):
        if v < b:
            return i
    return len(breaks)


def new_plate(plate, title, sub):
    fig = plt.figure(figsize=(12, 9), dpi=300)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([.045, .205, .91, .625])
    ax.set_facecolor(WATER)
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor(FRAME); sp.set_linewidth(0.8)
    fig.text(.045, .958, " ".join(plate), family=SANS, fontsize=8.4,
             color=MUTED, weight="demi")
    fig.text(.045, .912, title, family=SERIF, fontsize=23, color=INK)
    fig.text(.045, .876, sub, family=SANS, fontsize=10, color=INK2)
    fig.add_artist(plt.Line2D([.045, .955], [.856, .856], color=FRAME, lw=0.8))
    return fig, ax


def draw(ax, fills):
    pats, cols = [], []
    for ab, s in G.items():
        for ring in s["rings"]:
            pats.append(Polygon(ring, closed=True))
            cols.append(fills.get(ab, "#FFFFFF"))
    ax.add_collection(PatchCollection(pats, facecolor=cols, edgecolor="#FFFFFF",
                                      linewidths=0.7, zorder=2))


def label(ax, ab, text, color, size=8.6):
    x, y = CEN[ab]
    ax.text(x, y, text, ha="center", va="center", fontsize=size, family=SANS,
            weight="demi", color=color, zorder=6)


def callouts(ax, rows):
    """Stack off the northeast coast, sorted N->S so leaders never cross."""
    rows = sorted(rows, key=lambda r: -CEN[r[0]][1])
    x0, y0, dy, w, h = 2380000, 2520000, -150000, 560000, 104000
    for i, (ab, text, col, txtcol) in enumerate(rows):
        by = y0 + i*dy
        ax.add_patch(Rectangle((x0, by-h/2), w, h, facecolor=col,
                               edgecolor="#FFFFFF", lw=0.7, zorder=7))
        ax.text(x0+w/2, by, f"{ab}   {text}", ha="center", va="center",
                fontsize=8.2, family=SANS, weight="demi", color=txtcol, zorder=8)
        cx, cy = CEN[ab]
        ax.plot([cx, x0-25000], [cy, by], color="#9A948A", lw=0.55, zorder=5,
                solid_capstyle="round")
        ax.plot([cx], [cy], marker="o", ms=1.9, color="#9A948A", zorder=5)


def north_arrow(ax, x=-2300000, y=2760000):
    ax.plot([x, x], [y, y+215000], color=INK, lw=1.7, zorder=9)
    ax.add_patch(FancyArrow(x, y+150000, 0, 130000, width=0, head_width=76000,
                            head_length=92000, facecolor=INK, edgecolor=INK, zorder=9))
    ax.text(x, y-115000, "N", ha="center", va="center", fontsize=10.5,
            family=SANS, weight="demi", color=INK, zorder=9)


def legend(fig, entries, title, hatch_last=False):
    """Horizontal band in the margin below the map -- keeps the frame clear."""
    x, y = .045, .120
    fig.text(x, y + .042, title, family=SANS, fontsize=9.0, weight="demi", color=INK)
    for col, lab in entries:
        w = .0155
        r = Rectangle((x, y), w, .0225, transform=fig.transFigure, facecolor=col,
                      edgecolor="#FFFFFF", lw=0.7, figure=fig, zorder=10)
        fig.patches.append(r)
        if hatch_last and col == entries[-1][0]:
            fig.patches.append(Rectangle((x, y), w, .0225, transform=fig.transFigure,
                               facecolor="none", hatch="////", edgecolor="#C9C4B8",
                               lw=0.0, figure=fig, zorder=11))
        fig.text(x + w + .006, y + .0112, lab, family=SANS, fontsize=8.0,
                 color=INK2, va="center")
        x += w + .010 + .0072 * len(lab)


def note(ax, head, body, x=1830000, y=1400000):
    """Drawn in data space over the western Atlantic."""
    ax.text(x, y, head, family=SERIF, fontsize=12.5, color=INK, va="top", zorder=9)
    ax.text(x, y-175000, body, family=SANS, fontsize=8.0, color=INK2,
            va="top", linespacing=1.55, zorder=9)


def credits(fig, text):
    fig.add_artist(plt.Line2D([.045, .955], [.100, .100], color=FRAME, lw=0.8))
    fig.text(.045, .024, text, family=SANS, fontsize=7.0, color=MUTED,
             va="bottom", linespacing=1.7)


SRC_GEO = ("Projection  NAD83 / Conus Albers (EPSG:5070), equal area.   "
           "Boundaries  US Census Bureau cartographic boundary file, 2023, 1:20,000,000.")

# ═══════════════════════════════════════════════════════════ PLATE I - counts
def plate_one():
    BR = [1, 10, 25, 50, 100, 200]
    RAMP = ["#FFFFFF", "#E3ECF4", "#B9CFE4", "#82A7C9", "#4A7AA6", "#24537E", "#122F4B"]
    TXT  = [MUTED, INK2, INK2, INK, "#FFFFFF", "#FFFFFF", "#FFFFFF"]
    fig, ax = new_plate("PLATE II", "Preliminary tornado reports by state, 2026",
        "National Weather Service Local Storm Reports · 1 January – 13 August 2026")
    fills, cls = {}, {}
    for ab in G:
        v = S.get(ab, {}).get("lsr_2026", 0)
        cls[ab] = classify(v, BR); fills[ab] = RAMP[cls[ab]]
    draw(ax, fills)
    rows = []
    for ab in G:
        v = S.get(ab, {}).get("lsr_2026", 0)
        t = str(v) if v else "–"
        (rows.append((ab, t, RAMP[cls[ab]], TXT[cls[ab]])) if ab in CALLOUT
         else label(ax, ab, t, TXT[cls[ab]]))
    callouts(ax, rows); north_arrow(ax)
    legend(fig, [(RAMP[0], "none"), (RAMP[1], "1 – 9"), (RAMP[2], "10 – 24"),
                 (RAMP[3], "25 – 49"), (RAMP[4], "50 – 99"), (RAMP[5], "100 – 199"),
                 (RAMP[6], "200 or more")],
           "Reports  ·  classes rising by magnitude")
    note(ax, "These are reports, not tornadoes.",
         "One tornado crossing four counties files\n"
         "four reports. Against this year's completed\n"
         "damage surveys, Illinois' 283 reports\n"
         "correspond to roughly 135 tornadoes — a\n"
         "ratio of 0.48, third-lowest of the fifteen\n"
         "states with enough reports to measure.\n"
         "Plate III sets every state against its own\n"
         "history instead.")
    credits(fig,
        "Data  Iowa Environmental Mesonet, IEM Autoplot #163, preliminary and unfiltered Local Storm Reports, type TORNADO. Retrieved 22 August 2026.\n"
        + SRC_GEO + "\n"
        "Method  Classes rise by magnitude. Figures are counts of reports, not of tornadoes. Local Storm Reports are preliminary and are revised as damage surveys complete.   Plate by J. Kenny, 22 August 2026.")
    fig.savefig(B / "plate_II_reports_2026.png", facecolor=PAPER)
    fig.savefig(B / "plate_II_reports_2026.pdf", facecolor=PAPER)
    plt.close(fig); print("plate III written")


# ════════════════════════════════════════════════════════ PLATE II - anomaly
def plate_two():
    BR = [0.5, 0.8, 1.25, 2.0, 3.0]
    RAMP = ["#2B5580", "#8CADC9", "#EFEDE8", "#E3A98D", "#B25A32", "#8A3517"]
    TXT  = ["#FFFFFF", INK, INK2, INK, "#FFFFFF", "#FFFFFF"]
    GREY, MIN_BASE = "#E6E3DC", 5.0
    fig, ax = new_plate("PLATE III", "A displaced tornado season",
        "2026 reports against the same state's 2004–2025 average for 1 January – 13 August · Illinois runs at four times its own normal")
    fills, cls, masked = {}, {}, set()
    for ab in G:
        d = S.get(ab, {})
        if d.get("lsr_mean", 0) < MIN_BASE:
            masked.add(ab); fills[ab] = GREY; continue
        cls[ab] = classify(d["x_normal"], BR); fills[ab] = RAMP[cls[ab]]
    draw(ax, fills)
    for ab in masked:                      # pattern, so colour is not the only channel
        for ring in G[ab]["rings"]:
            ax.add_patch(Polygon(ring, closed=True, facecolor="none", hatch="////",
                                 edgecolor="#C9C4B8", lw=0.0, zorder=3))
    rows = []
    for ab in G:
        if ab in masked:
            t, col, tc = "n/a", GREY, INK2
        else:
            t, col, tc = f"{S[ab]['x_normal']:.1f}×", RAMP[cls[ab]], TXT[cls[ab]]
        (rows.append((ab, t, col, tc)) if ab in CALLOUT
         else label(ax, ab, t, tc, size=8.3))
    callouts(ax, rows); north_arrow(ax)
    legend(fig, [(RAMP[0], "below 0.5×"), (RAMP[1], "0.5 – 0.8×"),
                 (RAMP[2], "0.8 – 1.25×  near normal"), (RAMP[3], "1.25 – 2.0×"),
                 (RAMP[4], "2.0 – 3.0×"), (RAMP[5], "3.0× or more"),
                 (GREY, "base rate too low")],
           "2026 against its own 2004–2025 average", hatch_last=True)
    note(ax, "The alley is quiet. The corn belt is not.",
         "Texas sits at 0.38× its average, its\n"
         "21st-ranked year of 23. Florida is at\n"
         "0.23×, Tennessee 0.35×. Illinois, Indiana\n"
         "and Pennsylvania each set their highest\n"
         "count in the 23-year record. Nationally\n"
         "the season is 1.16× normal — the anomaly\n"
         "is in where the tornadoes went, not in\n"
         "how many there were.")
    credits(fig,
        "Data  Iowa Environmental Mesonet, IEM Autoplot #163, preliminary Local Storm Reports, type TORNADO, 2004–2026. Retrieved 22 August 2026.\n"
        + SRC_GEO + "\n"
        "Method  Each state is set against its own 2004–2025 mean for the identical window, so the map shows anomaly, not exposure. Classes are fixed multiples about a true midpoint of 1.0×; states averaging under five reports a year are masked.   Plate by J. Kenny, 22 August 2026.")
    fig.savefig(B / "plate_III_vs_normal_2026.png", facecolor=PAPER)
    fig.savefig(B / "plate_III_vs_normal_2026.pdf", facecolor=PAPER)
    plt.close(fig); print("plate II written")


plate_one(); plate_two()
