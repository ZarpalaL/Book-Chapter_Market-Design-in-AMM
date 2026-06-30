import os
import numpy as np
import matplotlib

# Try an interactive backend first so users can see the window.
for _backend in ("MacOSX", "TkAgg", "QtAgg"):
    try:
        matplotlib.use(_backend, force=True)
        break
    except Exception:
        continue
else:
    # Fallback for headless environments (still saves files)
    matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

pdf_path = os.path.join(OUT_DIR, "figure_2_2_IL_final.pdf")
png_path = os.path.join(OUT_DIR, "figure_2_2_IL_final.png")

# Example 2.2 — Uniform liquidity & impermanent loss
x0, y0 = 2_000_000.0, 1_000.0
k = x0 * y0
phi = 0.003
lp_s = 0.10
P0 = x0 / y0
lp_usdc0 = lp_s * x0
lp_eth0 = lp_s * y0

# Fee-adjusted trade
dy_trade = 100.0
dx_trade = x0 * dy_trade / ((1 - phi) * (y0 - dy_trade))
xp = x0 + dx_trade
yp = y0 - dy_trade
P1 = xp / yp

# Fee-adjusted marker values
V_actual_P1 = lp_s * 2 * xp
VHODL_P1 = lp_eth0 * P1 + lp_usdc0
IL_abs_P1 = V_actual_P1 - VHODL_P1
IL_pct_P1 = IL_abs_P1 / VHODL_P1 * 100

# Continuous no-fee curves
P_range = np.linspace(200, 7_000, 2_000)
V_lp = lp_s * 2 * np.sqrt(k * P_range)
V_hodl = lp_eth0 * P_range + lp_usdc0

# Correct IL formula (always <= 0, zero at P0)
ratio = P_range / P0
IL_curve = (2 * np.sqrt(ratio) / (1 + ratio) - 1) * 100

# Figure setup
fig, ax = plt.subplots(figsize=(9.5, 6.5))

# Grayscale palette
COL_CURVE = "#1f1f1f"
COL_HODL = "#4a4a4a"
COL_IL = "#707070"
COL_PRE = "#2f2f2f"
COL_GRID = "#d6d6d6"
BG = "#f7f7f7"

fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.grid(True, color=COL_GRID, lw=0.7, linestyle="--", alpha=0.8)
ax.set_axisbelow(True)
for sp in ax.spines.values():
    sp.set_color("#cccccc")
ax.tick_params(labelsize=9, color="#999999")

# Right axis for IL
ax_il = ax.twinx()
ax_il.set_facecolor(BG)
for sp in ax_il.spines.values():
    sp.set_color("#cccccc")
ax_il.spines["right"].set_color(COL_IL)
ax_il.tick_params(labelsize=9, colors=COL_IL)

# Main curves
ax.plot(
    P_range,
    V_lp,
    color=COL_CURVE,
    lw=2.4,
    zorder=4,
    label=r"LP portfolio value  $V(P) = 0.1 \times 2\sqrt{kP}$",
)
ax.plot(
    P_range,
    V_hodl,
    color=COL_HODL,
    lw=2.0,
    linestyle="--",
    dashes=(7, 4),
    zorder=4,
    label=r"HODL value  $W(P) = 100P + 200{,}000$",
)

# IL curve (right axis)
ax_il.plot(
    P_range,
    IL_curve,
    color=COL_IL,
    lw=1.8,
    linestyle="-.",
    dashes=(5, 3, 1, 3),
    zorder=3,
    alpha=0.9,
    label="Impermanent Loss (IL %)",
)
ax_il.axhline(0, color="#aaaaaa", lw=0.9, linestyle=":", alpha=0.7, zorder=2)

# P0 marker
V0 = lp_s * 2 * np.sqrt(k * P0)
ax.scatter([P0], [V0], s=90, color=COL_PRE, marker="o", zorder=7, edgecolors="white", lw=1.2)
ax.axvline(P0, color=COL_PRE, lw=0.9, linestyle=":", alpha=0.6, zorder=2)
ax.annotate(
    "$P_0 = 2{,}000$ USDC/ETH\nPortfolio value: $\\$400{,}000$\nIL = 0",
    xy=(P0, V0),
    xytext=(P0 - 1_100, V0 + 50_000),
    fontsize=8.8,
    color=COL_PRE,
    ha="left",
    va="bottom",
    arrowprops=dict(arrowstyle="-", color=COL_PRE, lw=0.8, shrinkB=4),
    bbox=dict(boxstyle="round,pad=0.3", facecolor=BG, edgecolor=COL_PRE, lw=0.9, alpha=0.95),
    zorder=8,
)

# P1 markers
ax.scatter([P1], [V_actual_P1], s=80, color=COL_IL, marker="o", zorder=7, edgecolors="white", lw=1.2)
ax.scatter([P1], [VHODL_P1], s=85, color=COL_IL, marker="D", zorder=7, edgecolors="white", lw=1.2)
ax.axvline(P1, color=COL_IL, lw=0.9, linestyle=":", alpha=0.5, zorder=2)

# Shaded IL gap
ax.fill_between(
    [P1 - 70, P1 + 70],
    [V_actual_P1, V_actual_P1],
    [VHODL_P1, VHODL_P1],
    color=COL_IL,
    alpha=0.12,
    zorder=2,
)

# Double arrow for gap
ax.annotate("", xy=(P1, V_actual_P1), xytext=(P1, VHODL_P1), arrowprops=dict(arrowstyle="<->", color=COL_IL, lw=1.3))

# Annotation box
ax.annotate(
    r"$P_{1}=2{,}469.88\ \mathrm{USDC/ETH}$"
    "\n"
    r"$\mathrm{HODL\ value}\ W(P_{1}) = 446{,}987.89$"
    "\n"
    r"$\mathrm{LP\ value}\ V(P_{1}) = 444{,}578.18$"
    "\n"
    r"$\mathrm{IL} = -2{,}409.71\ (-0.54\%)$",
    xy=(P1, V_actual_P1),
    xytext=(P1 + 600, V_actual_P1 - 110_000),
    fontsize=8.8,
    color=COL_IL,
    ha="left",
    va="top",
    arrowprops=dict(arrowstyle="-", color=COL_IL, lw=0.8, shrinkB=4),
    bbox=dict(boxstyle="round,pad=0.35", facecolor=BG, edgecolor=COL_IL, lw=0.9, alpha=0.96),
    zorder=8,
)

# Use one canonical set of corrected values
lp_value   = 444_578.18
hodl_value = 446_987.89
il_value   = -2_409.71
il_pct     = -0.54  # percent

summary_text = (
    f"LP Value: ${lp_value:,.2f}\n"
    f"HODL: ${hodl_value:,.2f}\n"
    f"IL: ${il_value:,.2f}\n"
    f"IL%: {il_pct:.2f}%"
)

# Ensure highlighted P1 point/label uses the same values
p1_y = lp_value
p1_label = (
    f"P1\nLP ${lp_value:,.2f}\n"
    f"HODL ${hodl_value:,.2f}\n"
    f"IL ${il_value:,.2f} ({il_pct:.2f}%)"
)

# Axes formatting
ax.set_xlim(400, 7_000)
ax.set_ylim(80_000, 820_000)
ax.set_xlabel("ETH price  $P$  (USDC per ETH)", fontsize=11, labelpad=7, color="#333333")
ax.set_ylabel("Portfolio value  (USDC)", fontsize=11, labelpad=7, color="#333333")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}k"))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))

ax_il.set_ylabel("Impermanent loss  (%)", fontsize=11, color=COL_IL, labelpad=7)
ax_il.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
ax_il.set_ylim(-30, 1)

# Legend
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax_il.get_legend_handles_labels()
ax.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc="lower right",
    fontsize=8.5,
    framealpha=0.94,
    edgecolor="#cccccc",
    facecolor=BG,
)

# Title
ax.set_title(
    "Liquidity provider value versus HODL benchmark\n"
    r"USDC/ETH pool ($k=2\times10^9$, fee = 0.3%, LP share = 10%)",
    fontsize=9.8,
    color="#222222",
    pad=10,
)

plt.tight_layout(pad=1.3)
plt.savefig(pdf_path, format="pdf", dpi=300, bbox_inches="tight", facecolor=BG)
plt.savefig(png_path, format="png", dpi=200, bbox_inches="tight", facecolor=BG)
print(f"Saved: {pdf_path}")
print(f"Saved: {png_path}")

if __name__ == "__main__":
    if "agg" not in plt.get_backend().lower():
        plt.show()
    else:
        print("Non-interactive backend active; figure saved to disk.")