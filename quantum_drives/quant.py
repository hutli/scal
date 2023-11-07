import json
import random
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy
import loguru
from matplotlib import ticker
from matplotlib.patches import FancyBboxPatch
import utils

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
    ("ARC <> CRU", 42_307_000_000),
    ("CRU <> HUR", 32_916_000_000),
    ("CRU <> MIC", 57_481_000_000),
    ("ARC <> HUR", 22_882_000_000),
    ("HUR <> MIC", 38_407_000_000),
    ("ARC <> MIC", 59_464_000_000),
    (
        "Earth <> Mars (Min)",
        54_600_000_000,
    ),  # For refence and fun - Stanton is really small 😅
    # ("Salvage (and back)", 90_000_000_000),
]

BEST_IN_SHOW = ["xl1", "voyage", "vk00", "ts2", "atlas", "spectre"]

STEP = 10_000_000
X_MIN = 0
X_MAX = 60_000_000_000

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
S1_QTNK_OVERRIDES = [(700, "125a"), (1960, "Cutter")]

QDRIVE_SIZES = json.load(open("qdrive_sizes.json"))


attachable_components = json.load(open("dump.json"))
QDRIVES = [v for k, v in attachable_components.items() if k.startswith("QDRV_")]
TANK_SIZES = {}
for k, v in attachable_components.items():
    if k.startswith("QTNK_"):
        ship_name = k.split("_", 2)[-1].replace("_", " ")
        capacity = round(utils.sc_key(v, "SCItemFuelTankParams")["capacity"])

        if ship_name == "Default":
            continue

        if not (
            size := next(
                (size for size, name in QDRIVE_SIZES if name in ship_name.lower()),
                None,
            )
        ):
            loguru.logger.error(f'"{ship_name}" not in QDRIVE_SIZES!')
            exit()
        if any(n for _, n in S1_QTNK_OVERRIDES if n.lower() == ship_name.lower()):
            loguru.logger.info(f'"{ship_name}" in overrides, skipping game file')
            continue

        if size not in TANK_SIZES:
            TANK_SIZES[size] = {}

        if capacity not in TANK_SIZES[size]:
            TANK_SIZES[size][capacity] = []

        if capacity == 583:
            ship_name = "Most S1 ships"
        TANK_SIZES[size][capacity].append(ship_name)
        TANK_SIZES[size][capacity] = list(set(TANK_SIZES[size][capacity]))

for capacity, ship_name in S1_QTNK_OVERRIDES:
    if capacity not in TANK_SIZES[size]:
        TANK_SIZES[size][capacity] = []
    TANK_SIZES[size][capacity].append(ship_name)
    TANK_SIZES[size][capacity] = list(set(TANK_SIZES[size][capacity]))

x = list(range(X_MIN, X_MAX, STEP))


def create_fig(
    qdrives,
    figure_title,
    file_name,
    tank_sizes=[],
    show_size=False,
    subtitle='Travel time (including spool up time) for any realistic distance in Stanton given each quantum drive (Remeber: Lower time is better)\nData has been extracted directly from the 3.21.0 game files via "scdatatools" (https://gitlab.com/scmodding/frameworks/scdatatools).\nCalculations are based on the paper "A study on travel time and the underlying physical model of Quantum Drives in Star Citizen" by @Erec (https://gitlab.com/Erecco/a-study-on-quantum-travel-time).',
):
    # Initialize layout ----------------------------------------------
    fig, ax = plt.subplots(figsize=(22, 11))

    # Background color
    fig.patch.set_facecolor(GREY98)
    ax.set_facecolor(GREY98)

    random.shuffle(COLORS)

    qdrives = sorted(
        qdrives,
        key=lambda q: utils.calc_t_tot(
            utils.sc_key(q, "SCItemQuantumDriveParams")["params"]["driveSpeed"],
            utils.sc_key(q, "SCItemQuantumDriveParams")["params"]["stageOneAccelRate"],
            utils.sc_key(q, "SCItemQuantumDriveParams")["params"]["stageTwoAccelRate"],
            x[-1],
            utils.sc_key(q, "SCItemQuantumDriveParams")["params"]["spoolUpTime"],
        ),
    )
    LABELS = sorted(
        [
            (
                utils.get_name(q, show_size),
                utils.calc_t_tot(
                    utils.sc_key(q, "SCItemQuantumDriveParams")["params"]["driveSpeed"],
                    utils.sc_key(q, "SCItemQuantumDriveParams")["params"][
                        "stageOneAccelRate"
                    ],
                    utils.sc_key(q, "SCItemQuantumDriveParams")["params"][
                        "stageTwoAccelRate"
                    ],
                    x[-1],
                    utils.sc_key(q, "SCItemQuantumDriveParams")["params"][
                        "spoolUpTime"
                    ],
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
    loguru.logger.debug(len(LABELS))

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
        params = utils.sc_key(qdrive, "SCItemQuantumDriveParams")["params"]

        y = [
            utils.calc_t_tot(
                params["driveSpeed"],
                params["stageOneAccelRate"],
                params["stageTwoAccelRate"],
                d_tot,
                params["spoolUpTime"],
            )
            for d_tot in x
        ]

        ax.plot(x, y, linewidth=0.8, color=COLORS[i])

        fuel_requirement = utils.sc_key(qdrive, "SCItemQuantumDriveParams")[
            "quantumFuelRequirement"
        ]
        for ii, (size, _) in enumerate(tank_sizes):
            max_range = size / fuel_requirement * 1_000_000
            tank_x = min(X_MAX, max_range)
            tank_y = utils.calc_t_tot(
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
                fontsize=5,
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
        for q in QDRIVES
        if utils.sc_key(q, "SAttachableComponentParams")["AttachDef"]["Size"] == 1
    ],
    f"Size 1 quantum drives - including maximum ranges",
    "results/res1",
    tank_sizes=sorted([(k, ", ".join(v)) for k, v in TANK_SIZES[1].items()]),
    subtitle='Travel time (including spool up time) for any realistic distance in Stanton given each quantum drive (Remeber: Lower time is better)\nNumbers has been placed at the point when each size 1 quantum fuel tank runs out of fuel, i.e. that tanks/ships maximum range with the specific quantum drive (see legend)\nData has been extracted directly from the 3.21.0 game files via "scdatatools" (https://gitlab.com/scmodding/frameworks/scdatatools).\nCalculations are based on the paper "A study on travel time and the underlying physical model of Quantum Drives in Star Citizen" by @Erec (https://gitlab.com/Erecco/a-study-on-quantum-travel-time).',
)
create_fig(
    [
        q
        for q in QDRIVES
        if utils.sc_key(q, "SAttachableComponentParams")["AttachDef"]["Size"] == 1
    ],
    f"Size 1 quantum drives",
    "results/res1_alt",
)
create_fig(
    [
        q
        for q in QDRIVES
        if utils.sc_key(q, "SAttachableComponentParams")["AttachDef"]["Size"] == 2
    ],
    f"Size 2 quantum drives",
    "results/res2",
)
create_fig(
    [
        q
        for q in QDRIVES
        if utils.sc_key(q, "SAttachableComponentParams")["AttachDef"]["Size"] == 3
    ],
    f"Size 3 quantum drives",
    "results/res3",
)
create_fig(
    [
        q
        for q in QDRIVES
        if any(
            [
                n
                for n in BEST_IN_SHOW
                if utils.sc_key(q, "SAttachableComponentParams")["AttachDef"][
                    "Localization"
                ]["Name"]
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
