import json
import random
from datetime import timedelta
from math import acos, cos, cosh, log, sqrt

import matplotlib.pyplot as plt
import numpy
from matplotlib import ticker
from matplotlib.patches import FancyBboxPatch

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

BEST_IN_SHOW = ["xl1", "voyage", "vk00", "ts2", "atlas", "spectre"]

with open("qdrives.json") as f:
    qdrives = json.load(f)

STEP = 10_000_000
X_MIN = 0
X_MAX = 70_000_000_000

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


def calc_t_tot(v_max, a_1, a_2, d_tot, k):
    if calc_d_c(v_max, a_1, a_2, d_tot) < 0:
        z = calc_z(v_max, a_1, a_2, d_tot)
        if z > 1:
            return ((4 * a_1 * v_max) / (a_2**2 - a_1**2)) * (
                2 * cosh(1 / 3 * log(z - sqrt(z**2 - 1))) - 1
            ) + k
        acos_arg = (3 * (a_2 - a_1) ** 2 * (a_1 + a_2) ** 2 * d_tot) / (
            8 * a_1**3 * v_max**2
        ) - 1
        return (4 * a_1 * v_max) / (a_2**2 - a_1**2) * (
            2 * cos((1 / 3) * acos(acos_arg)) - 1
        ) + k
    else:
        return (
            (4 * v_max) / (a_1 + a_2)
            + d_tot / v_max
            - (4 * v_max * (2 * a_1 + a_2)) / (3 * (a_1 + a_2) ** 2)
            + k
        )


def sc_key(obj, key, second_key="Components"):
    return next(c for c in obj[second_key] if key in c.keys())[key]


def create_fig(
    qdrives,
    figure_title,
    file_name,
    tank_sizes=[],
    show_size=False,
    subtitle='Travel time (including spool up time) for any realistic distance in Stanton given each quantum drive (Remeber: Lower time is better)\nData has been extracted directly from the 3.19.1 game files via "scdatatools" (https://gitlab.com/scmodding/frameworks/scdatatools).\nCalculations are based on the paper "A study on travel time and the underlying physical model of Quantum Drives in Star Citizen" by @Erec (https://gitlab.com/Erecco/a-study-on-quantum-travel-time).',
):
    # Initialize layout ----------------------------------------------
    fig, ax = plt.subplots(figsize=(22, 11))

    # Background color
    fig.patch.set_facecolor(GREY98)
    ax.set_facecolor(GREY98)

    random.shuffle(COLORS)

    qdrives = sorted(
        qdrives,
        key=lambda q: calc_t_tot(
            sc_key(q, "SCItemQuantumDriveParams")["params"]["driveSpeed"],
            sc_key(q, "SCItemQuantumDriveParams")["params"]["stageOneAccelRate"],
            sc_key(q, "SCItemQuantumDriveParams")["params"]["stageTwoAccelRate"],
            x[-1],
            sc_key(q, "SCItemQuantumDriveParams")["params"]["spoolUpTime"],
        ),
    )
    LABELS = sorted(
        [
            (
                sc_key(q, "SAttachableComponentParams")["AttachDef"]["Localization"][
                    "Name"
                ]
                .replace("_SCItem", "")
                .rsplit("_", 1)[-1]
                + (
                    f'({sc_key(q,"SAttachableComponentParams")["AttachDef"]["Size"]})'
                    if show_size
                    else ""
                ),
                calc_t_tot(
                    sc_key(q, "SCItemQuantumDriveParams")["params"]["driveSpeed"],
                    sc_key(q, "SCItemQuantumDriveParams")["params"][
                        "stageOneAccelRate"
                    ],
                    sc_key(q, "SCItemQuantumDriveParams")["params"][
                        "stageTwoAccelRate"
                    ],
                    x[-1],
                    sc_key(q, "SCItemQuantumDriveParams")["params"]["spoolUpTime"],
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

    PAD = (X_MAX - X_MIN) * 0.05

    # Horizontal lines
    ax.hlines(y=range(0, int(MAX_Y), 60), xmin=X_MIN, xmax=X_MAX, color=GREY91, lw=0.6)
    ax.hlines(
        y=[i for i in range(0, int(MAX_Y), 30) if i % 60],
        xmin=X_MIN,
        xmax=X_MAX,
        color=GREY91,
        lw=0.6,
        linestyles="dashed",
    )

    # Vertical lines used as scale reference
    # for h in range(X_MIN, X_MAX, 10_000_000_000):
    #     ax.axvline(h, color=GREY91, lw=0.6, zorder=0)

    # Add labels for drives
    for i, (text, y_end, y_text) in enumerate(LABELS):
        # Vertical start of line
        y_start = 0

        # Add line based on three points
        ax.plot(
            [X_MAX, X_MAX + PAD / 4 * 3, X_MAX + PAD],
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
        params = sc_key(qdrive, "SCItemQuantumDriveParams")["params"]

        y = [
            calc_t_tot(
                params["driveSpeed"],
                params["stageOneAccelRate"],
                params["stageTwoAccelRate"],
                d_tot,
                params["spoolUpTime"],
            )
            for d_tot in x
        ]

        ax.plot(x, y, color=COLORS[i])

        fuel_requirement = sc_key(qdrive, "SCItemQuantumDriveParams")[
            "quantumFuelRequirement"
        ]
        for ii, (size, _) in enumerate(tank_sizes):
            max_range = size / fuel_requirement * 1_000_000
            tank_x = min(X_MAX, max_range)
            tank_y = calc_t_tot(
                params["driveSpeed"],
                params["stageOneAccelRate"],
                params["stageTwoAccelRate"],
                tank_x,
                params["spoolUpTime"],
            )
            plt.text(
                tank_x,
                tank_y,
                str(ii),
                color=COLORS[i],
                backgroundcolor=GREY98,
                fontsize=9,
                multialignment="center",
                verticalalignment="center",
                bbox=dict(facecolor=GREY98, edgecolor=GREY98, pad=0.0),
            )
            if max_range > X_MAX:
                break

        if tank_sizes:
            ax.legend(
                [
                    f"{ii}: {size} ({legend_text})"
                    for ii, (size, legend_text) in enumerate(tank_sizes)
                ],
                # handletextpad=-2.0,
                handlelength=0,
            )

    plt.ticklabel_format(style="plain")  # to prevent scientific notation.

    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}m"))
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"{x//60:2.0f}:{x%60:02.0f}")
    )
    plt.yticks(range(0, int(MAX_Y), 60))
    plt.yticks(range(0, int(MAX_Y), 30), minor=True)

    plt.suptitle(
        figure_title,
        fontsize=24,
    )
    plt.title(
        subtitle,
        fontsize=12,
    )

    plt.savefig(f"{file_name}.webp", dpi=600)
    plt.savefig(f"{file_name}.svg")


create_fig(
    [
        q
        for q in qdrives
        if sc_key(q, "SAttachableComponentParams")["AttachDef"]["Size"] == 1
    ],
    f"Size 1 quantum drives",
    "results/res1",
    tank_sizes=[
        (583.3300170898438, "Most S1 ships"),
        (625.0, "85X"),
        (645.0, "All Pisces"),
        (680.0, "300i"),
        (700.0, "Aurora LX, 100i, Mustang Beta"),
        (770.75, "Nomad"),
        (800.0, "Scorpius Antares"),
        (830.0, "315p"),
        (950.0, "Terrapin"),
        (1000.0, "Mantis"),
        (2750.0, "Defender"),
        (3000.0, "Cutter"),
        (10000.0, "Hull A"),
    ],
    subtitle='Travel time (including spool up time) for any realistic distance in Stanton given each quantum drive (Remeber: Lower time is better)\nNumbers has been placed at the point when each size 1 quantum fuel tank runs out of fuel, i.e. that tanks/ships maximum range with the specific quantum drive (see legend)\nData has been extracted directly from the 3.19.1 game files via "scdatatools" (https://gitlab.com/scmodding/frameworks/scdatatools).\nCalculations are based on the paper "A study on travel time and the underlying physical model of Quantum Drives in Star Citizen" by @Erec (https://gitlab.com/Erecco/a-study-on-quantum-travel-time).',
)
create_fig(
    [
        q
        for q in qdrives
        if sc_key(q, "SAttachableComponentParams")["AttachDef"]["Size"] == 2
    ],
    f"Size 2 quantum drives",
    "results/res2",
)
create_fig(
    [
        q
        for q in qdrives
        if sc_key(q, "SAttachableComponentParams")["AttachDef"]["Size"] == 3
    ],
    f"Size 3 quantum drives",
    "results/res3",
)
create_fig(
    [
        q
        for q in qdrives
        if any(
            [
                n
                for n in BEST_IN_SHOW
                if sc_key(q, "SAttachableComponentParams")["AttachDef"]["Localization"][
                    "Name"
                ]
                .replace("_SCItem", "")
                .rsplit("_", 1)[-1]
                .lower()
                in n.lower()
            ]
        )
    ],
    f"Common quantum drives",
    "results/resb",
    show_size=True,
)
