import json
import random
from datetime import timedelta
from math import acos, cos, cosh, log, sqrt

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy

# Shades of gray
GREY10 = "#1a1a1a"
GREY30 = "#4d4d4d"
GREY40 = "#666666"
GREY50 = "#7f7f7f"
GREY60 = "#999999"
GREY75 = "#bfbfbf"
GREY91 = "#e8e8e8"
GREY98 = "#fafafa"

DISTANCES = [
    ("ARC<->CRU", 42_307_000_000),
    ("CRU<->HUR", 32_916_000_000),
    ("CRU<->MIC", 57_481_000_000),
    ("ARC<->HUR", 22_882_000_000),
    ("HUR<->MIC", 38_407_000_000),
    ("ARC<->MIC", 59_464_000_000),
    (
        "Earth<->Mars (Min)",
        54_600_000_000,
    ),  # For refence and fun - Stanton is really small 😅
]

BEST_IN_SHOW = ["xl-1", "voyage", "vk-00", "ts-2", "atlas"]

with open("qdrives.json") as f:
    qdrives = json.load(f)

STEP = 100_000_000
X_MIN = STEP
X_MAX = 65_000_000_000

COLORS = [
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
    "#008080",
    "#e6beff",
    "#9a6324",
    "#c0c0c0",
    "#800000",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#000075",
    "#808080",
    "#404040",
    "#000000",
]

x = list(range(X_MIN, X_MAX, STEP))


# Here be dragons - read https://gitlab.com/Erecco/a-study-on-quantum-travel-time to understand
def calc_z(v_max, a_1, a_2, d_tot):
    return (3 * (a_2 - a_1) ** 2 * (a_1 + a_2) ** 2 * d_tot) / (
        8 * a_1**3 * v_max**2
    ) - 1


def calc_d_c(v_max, a_1, a_2, d_tot):
    return d_tot - (4 * v_max**2 * (2 * a_1 + a_2)) / (3 * (a_1 + a_2) ** 2)


def calc_t_tot(v_max, a_1, a_2, d_tot):
    if calc_d_c(v_max, a_1, a_2, d_tot) < 0:
        z = calc_z(v_max, a_1, a_2, d_tot)
        if z > 1:
            return ((4 * a_1 * v_max) / (a_2**2 - a_1**2)) * (
                2 * cosh(1 / 3 * log(z - sqrt(z**2 - 1))) - 1
            )
        acos_arg = (3 * (a_2 - a_1) ** 2 * (a_1 + a_2) ** 2 * d_tot) / (
            8 * a_1**3 * v_max**2
        ) - 1
        return (
            (4 * a_1 * v_max)
            / (a_2**2 - a_1**2)
            * (2 * cos((1 / 3) * acos(acos_arg)) - 1)
        )
    else:
        return (
            (4 * v_max) / (a_1 + a_2)
            + d_tot / v_max
            - (4 * v_max * (2 * a_1 + a_2)) / (3 * (a_1 + a_2) ** 2)
        )


def create_fig(qdrives, figure_title, file_name, show_size=False):
    # Initialize layout ----------------------------------------------
    fig, ax = plt.subplots(figsize=(22, 11))

    # Background color
    fig.patch.set_facecolor(GREY98)
    ax.set_facecolor(GREY98)

    random.shuffle(COLORS)

    qdrives = sorted(
        qdrives,
        key=lambda q: calc_t_tot(
            q["data"]["qdrive"]["params"]["driveSpeed"],
            q["data"]["qdrive"]["params"]["stageOneAccelRate"],
            q["data"]["qdrive"]["params"]["stageTwoAccelRate"],
            x[-1],
        ),
    )
    LABELS = sorted(
        [
            (
                q["data"]["name"] + (f'({q["data"]["size"]})' if show_size else ""),
                calc_t_tot(
                    q["data"]["qdrive"]["params"]["driveSpeed"],
                    q["data"]["qdrive"]["params"]["stageOneAccelRate"],
                    q["data"]["qdrive"]["params"]["stageTwoAccelRate"],
                    x[-1],
                ),
            )
            for q in qdrives
        ],
        key=lambda q: q[1],
    )

    MAX_Y = max(t for _, t in LABELS)
    LOWEST_MAX_Y = min(t for _, t in LABELS)

    LABELS = [
        (h, t, LOWEST_MAX_Y + i * ((MAX_Y - LOWEST_MAX_Y) / (len(LABELS) - 1)))
        for i, (h, t) in enumerate(LABELS)
    ]
    print(len(LABELS))

    PAD = (X_MAX - X_MIN) * 0.03

    # Horizontal lines
    ax.hlines(y=range(0, int(MAX_Y), 100), xmin=X_MIN, xmax=X_MAX, color=GREY91, lw=0.6)

    # Vertical lines used as scale reference
    # for h in range(X_MIN, X_MAX, 10_000_000_000):
    #     ax.axvline(h, color=GREY91, lw=0.6, zorder=0)

    # Add labels for drives
    for i, (text, y_end, y_text) in enumerate(LABELS):
        # Vertical start of line
        y_start = 0

        # Add line based on three points
        ax.plot(
            [X_MAX, X_MAX + PAD / 3 * 2, X_MAX + PAD],
            [y_end, y_text, y_text],
            alpha=0.5,
            ls="dashed",
            color=COLORS[i],
        )

        # Add drive text
        ax.text(
            X_MAX + PAD,
            y_text,
            text,
            fontsize=9,
            weight="bold",
            # fontfamily="Montserrat",
            va="center",
        )

    for name, dist in DISTANCES:
        # Vertical like for distance
        ax.axvline(dist, color=GREY40, ls="dotted")

        # Annotations for distance
        ax.text(
            dist - X_MAX * 0.012,
            0,
            name,
            fontsize=14,
            fontweight=500,
            color=GREY40,
            ha="left",
            rotation=90,
        )

    for i, qdrive in enumerate(qdrives):
        params = qdrive["data"]["qdrive"]["params"]

        y = [
            calc_t_tot(
                params["driveSpeed"],
                params["stageOneAccelRate"],
                params["stageTwoAccelRate"],
                d_tot,
            )
            for d_tot in x
        ]

        ax.plot(x, y, color=COLORS[i])

    plt.ticklabel_format(style="plain")  # to prevent scientific notation.

    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}m"))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}s"))

    plt.suptitle(
        figure_title,
        fontsize=24,
    )
    plt.title(
        'Travel time (in seconds) for any realistic distance in Stanton (in meters) given each quantum drive in Star Citizen.\nRemeber: Lower time is better!\nData has been extracted directly from the 3.19.1 game files.\nCalculations are based on the paper "A study on travel time and the underlying physical model of Quantum Drives in Star Citizen" by @Erec (https://gitlab.com/Erecco/a-study-on-quantum-travel-time).',
        fontsize=12,
    )

    plt.savefig(f"{file_name}.webp", dpi=600)
    plt.savefig(f"{file_name}.svg")


create_fig(
    [q for q in qdrives if q["data"]["size"] == 1],
    f"Size 1 quantum drives",
    "results/res1",
)
create_fig(
    [q for q in qdrives if q["data"]["size"] == 2],
    f"Size 2 quantum drives",
    "results/res2",
)
create_fig(
    [q for q in qdrives if q["data"]["size"] == 3],
    f"Size 3 quantum drives",
    "results/res3",
)
create_fig(
    [
        q
        for q in qdrives
        if any([n for n in BEST_IN_SHOW if q["data"]["name"].lower() in n.lower()])
    ],
    f"Common quantum drives",
    "results/resb",
    show_size=True,
)
