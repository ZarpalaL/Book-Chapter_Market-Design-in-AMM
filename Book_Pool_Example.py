import matplotlib
matplotlib.use("TkAgg")  # Interactive backend

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def main():
    # Given example (no fees)
    x = 2_000_000.0          # USDC reserve
    y = 1_000.0              # ETH reserve
    delta_x = 449_489.74     # USDC deposited by trader
    k = x * y                # invariant

    # Trade outcome (USDC in, ETH out)
    delta_y = (y * delta_x) / (x + delta_x)
    x_new = x + delta_x
    y_new = y - delta_y

    # Prices
    p_spot_pre = x / y
    p_effective = delta_x / delta_y
    p_spot_post = x_new / y_new

    # Price impact (USDC)
    expected_cost_at_pre_spot = delta_y * p_spot_pre
    price_impact = delta_x - expected_cost_at_pre_spot

    # Print checks
    print("=== Uniswap v2 Example (No Fee) ===")
    print(f"k = {k:,.0f}")
    print(f"Pre-trade spot price p^s = {p_spot_pre:,.2f} USDC/ETH")
    print(f"Delta_x = {delta_x:,.2f} USDC")
    print(f"Delta_y = {delta_y:,.4f} ETH")
    print(f"Effective price p^e = {p_effective:,.2f} USDC/ETH")
    print(f"Price impact = {price_impact:,.2f} USDC")
    print(f"x' = {x_new:,.2f}, y' = {y_new:,.4f}")
    print(f"Post-trade spot price p^s' = {p_spot_post:,.2f} USDC/ETH")

    # Invariant curve: x = k / y  (x-axis is ETH reserves y)
    y_vals = np.linspace(300, 4000, 2000)
    x_vals = k / y_vals

    fig, ax = plt.subplots(figsize=(9, 5))

    # Dashed segment only between pre/post states
    y_start, y_end = sorted([y_new, y])
    mask_left = y_vals < y_start
    mask_mid = (y_vals >= y_start) & (y_vals <= y_end)
    mask_right = y_vals > y_end

    ax.plot(y_vals[mask_left], x_vals[mask_left], color="steelblue", lw=1.4, label="Invariant curve")
    ax.plot(y_vals[mask_mid], x_vals[mask_mid], color="steelblue", lw=1.4, ls="--")
    ax.plot(y_vals[mask_right], x_vals[mask_right], color="steelblue", lw=1.4)

    # Pre/Post points
    ax.scatter([y], [x], s=12, color="green", zorder=6, label="Pre-trade spot")
    ax.text(
        y + 35, x + 10_000,
        r"$p^{\mathrm{s}}_{x/y}=2000$",
        color="green",
        fontsize=11
    )

    ax.scatter([y_new], [x_new], s=12, color="red", zorder=6, label="Post-trade spot")
    ax.text(
        y_new + 35, x_new + 10_000,
        rf"$p_{{x/y}}^{{\mathrm{{s}}\prime}}\approx {p_spot_post:,.0f}$",
        color="red",
        fontsize=11
    )

    # Reserve guide lines
    guide_kw = dict(colors="gray", linestyles="--", lw=1.0, alpha=0.55)
    ax.vlines(y, ymin=0, ymax=x, **guide_kw)
    ax.hlines(x, xmin=300, xmax=y, **guide_kw)
    ax.vlines(y_new, ymin=0, ymax=x_new, **guide_kw)
    ax.hlines(x_new, xmin=300, xmax=y_new, **guide_kw)

    # Optional tangent at pre-trade point
    slope = -x / y
    dy_tan = 300                       # was smaller
    y_tan = np.array([y - dy_tan, y + dy_tan])
    x_tan = x + slope * (y_tan - y)
    ax.plot(
        y_tan, x_tan,
        color="darkorange",
        lw=1.2,
        ls="--",
        zorder=5,
        label="Tangent line (pre-trade)"
    )

    # Axis and formatting
    ax.set_xlim(300, 4000)
    ax.set_ylim(0, 4_000_000)
    ax.set_title("Constant-Product Invariant and Pool Adjustment in a Uniswap v2 USDC/ETH Pool")
    ax.set_xlabel("ETH reserves (y)")
    ax.set_ylabel("USDC reserves (x)")
    ax.grid(True, alpha=0.25)
    ax.legend()

    ax.ticklabel_format(style="plain", axis="both")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    # Keep existing ticks and force-insert post-trade ETH reserve on x-axis
    xticks = list(ax.get_xticks())
    xticks.append(y_new)
    xticks = sorted(set(round(t, 4) for t in xticks))
    ax.set_xticks(xticks)

    # Build ticks, then remove any tick too close to y_new
    xticks = list(ax.get_xticks())
    xticks = [t for t in xticks if abs(t - y_new) > 20]  # tolerance in x-axis units
    xticks.append(y_new)
    xticks = sorted(xticks)
    ax.set_xticks(xticks)

    # Label only one post-trade tick as 816.5
    ax.set_xticklabels(["816.5" if abs(t - y_new) < 1e-6 else f"{t:,.0f}" for t in xticks])

    # Optional: show only integer tick labels (clean)
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    # Smaller tick label fonts
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=8)

    # Optional: slight rotation to avoid overlap on x-axis
    for lbl in ax.get_xticklabels():
        lbl.set_rotation(20)
        lbl.set_ha("right")

    # 1) Force post-trade x-axis tick label to show exactly 816.5
    xticks = sorted(set(list(ax.get_xticks()) + [y_new]))
    ax.set_xticks(xticks)
    ax.set_xticklabels(["816.5" if abs(t - y_new) < 1e-6 else f"{t:,.0f}" for t in xticks])

    # 2) Dashed guide lines from each spot to BOTH axes
    guide_kw = dict(colors="gray", linestyles="--", lw=1.1, alpha=0.65)

    # Pre-trade spot (y, x)
    ax.vlines(y, ymin=0, ymax=x, **guide_kw)      # to x-axis
    ax.hlines(x, xmin=0, xmax=y, **guide_kw)      # to y-axis

    # Post-trade spot (y_new, x_new)
    ax.vlines(y_new, ymin=0, ymax=x_new, **guide_kw)   # to x-axis
    ax.hlines(x_new, xmin=0, xmax=y_new, **guide_kw)   # to y-axis

    plt.tight_layout()
    plt.savefig("pool_example_graph_adjusted.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    main()
