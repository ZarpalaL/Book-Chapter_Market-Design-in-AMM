import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ============================================================
# Helper: draw an "exchange-like" ORDER BOOK LADDER (LIGHT THEME)
# (bids on left, asks on right, colored depth bars behind rows)
# ============================================================
def plot_order_book_ladder(
    bid_prices, bid_sizes,
    ask_prices, ask_sizes,
    title="ETH-USDC Order Book (Ladder)",
    n_levels=18
):
    # --- sort like a real book
    bid_idx = np.argsort(-bid_prices)          # bids high -> low
    ask_idx = np.argsort(ask_prices)           # asks low  -> high
    bid_prices, bid_sizes = bid_prices[bid_idx], bid_sizes[bid_idx]
    ask_prices, ask_sizes = ask_prices[ask_idx], ask_sizes[ask_idx]

    # --- keep top n_levels
    n = min(n_levels, len(bid_prices), len(ask_prices))
    bp, bs = bid_prices[:n], bid_sizes[:n]
    ap, aqs = ask_prices[:n], ask_sizes[:n]

    # --- normalize bar widths by max size visible
    max_size = max(bs.max(), aqs.max())
    bw = bs / max_size
    aw = aqs / max_size

    # --- figure / axes (light UI)
    fig, ax = plt.subplots(figsize=(7.2, 9))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n + 2)
    ax.axis("off")

    # Column x positions
    x_left_amt  = 0.06
    x_mid_price = 0.50
    x_right_amt = 0.94

    # Bars fill toward the center
    x_center = 0.50
    left_bar_max  = 0.42
    right_bar_max = 0.42

    # Header
    ax.text(0.5, n + 1.35, title, ha="center", va="center",
            color="#111111", fontsize=14, fontweight="bold")

    ax.text(x_left_amt,  n + 0.6, "Amount (ETH)", ha="left",  va="center",
            color="#4b5563", fontsize=10)
    ax.text(x_mid_price, n + 0.6, "Bid (USD)     Ask (USD)", ha="center", va="center",
            color="#4b5563", fontsize=10)
    ax.text(x_right_amt, n + 0.6, "Amount (ETH)", ha="right", va="center",
            color="#4b5563", fontsize=10)

    # Row geometry
    row_h = 0.8
    y0 = n  # top row start

    # Colors
    bid_bar_color = "#00c084"
    ask_bar_color = "#ff4d5a"
    bid_text = "#00a36f"
    ask_text = "#e03a47"
    text_main = "#111111"

    # Draw rows
    for i in range(n):
        y = y0 - i

        # subtle row separators
        ax.plot([0.04, 0.96], [y - row_h/2, y - row_h/2], color="#e5e7eb", lw=0.8)

        # Bid bar (fills left from center)
        bid_w = left_bar_max * bw[i]
        ax.add_patch(Rectangle((x_center - bid_w, y - row_h/2),
                               bid_w, row_h * 0.85,
                               facecolor=bid_bar_color, alpha=0.18, edgecolor="none"))

        # Ask bar (fills right from center)
        ask_w = right_bar_max * aw[i]
        ax.add_patch(Rectangle((x_center, y - row_h/2),
                               ask_w, row_h * 0.85,
                               facecolor=ask_bar_color, alpha=0.18, edgecolor="none"))

        # Left amount (bid size)
        ax.text(x_left_amt, y, f"{bs[i]:.6f}", ha="left", va="center",
                color=text_main, fontsize=10)

        # Mid prices
        ax.text(x_center - 0.01, y, f"{bp[i]:,.2f}", ha="right", va="center",
                color=bid_text, fontsize=11, fontweight="bold")
        ax.text(x_center + 0.01, y, f"{ap[i]:,.2f}", ha="left", va="center",
                color=ask_text, fontsize=11, fontweight="bold")

        # Right amount (ask size)
        ax.text(x_right_amt, y, f"{aqs[i]:.6f}", ha="right", va="center",
                color=text_main, fontsize=10)

    # Center divider
    ax.plot([x_center, x_center], [0.6, n + 0.2], color="#d1d5db", lw=1.2)

    plt.tight_layout()
    plt.show()


# ============================================================
# Helper: draw an "exchange-like" DEPTH CHART (LIGHT THEME)
# (green cumulative bids on left, red cumulative asks on right)
# ============================================================
def plot_depth_chart(
    bid_prices, bid_sizes,
    ask_prices, ask_sizes,
    title="Depth",
    n_levels=80
):
    # sort
    bid_idx = np.argsort(-bid_prices)
    ask_idx = np.argsort(ask_prices)
    bid_prices, bid_sizes = bid_prices[bid_idx], bid_sizes[bid_idx]
    ask_prices, ask_sizes = ask_prices[ask_idx], ask_sizes[ask_idx]

    # keep more levels for smoother depth
    bid_prices, bid_sizes = bid_prices[:n_levels], bid_sizes[:n_levels]
    ask_prices, ask_sizes = ask_prices[:n_levels], ask_sizes[:n_levels]

    # cumulative depth
    bid_cum = np.cumsum(bid_sizes)
    ask_cum = np.cumsum(ask_sizes)

    best_bid = bid_prices[0]
    best_ask = ask_prices[0]
    mid = 0.5 * (best_bid + best_ask)

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Depth curves + fill
    ax.step(bid_prices[::-1], bid_cum[::-1], where="post", lw=2, color="#00c084")
    ax.fill_between(bid_prices[::-1], bid_cum[::-1], step="post", alpha=0.18, color="#00c084")

    ax.step(ask_prices, ask_cum, where="post", lw=2, color="#ff4d5a")
    ax.fill_between(ask_prices, ask_cum, step="post", alpha=0.18, color="#ff4d5a")

    # Mid marker
    ax.axvline(mid, color="#6b7280", lw=1, ls="--", alpha=0.8)

    # Light theme styling
    ax.set_title(title, color="#111111", loc="left", pad=10, fontsize=12, fontweight="bold")
    ax.tick_params(colors="#374151")
    for spine in ax.spines.values():
        spine.set_color("#d1d5db")

    ax.set_xlabel("Price (USDC per ETH)", color="#374151")
    ax.set_ylabel("Cumulative size (ETH)", color="#374151")

    # Tight x-limits around book
    x_min = min(bid_prices.min(), ask_prices.min())
    x_max = max(bid_prices.max(), ask_prices.max())
    pad = 0.02 * (x_max - x_min + 1e-9)
    ax.set_xlim(x_min - pad, x_max + pad)

    plt.tight_layout()
    plt.show()


# ============================================================
# Example data (generated deeper book for smoother visuals)
# ============================================================
np.random.seed(7)

n_levels = 60
tick = 0.01
best_bid = 2048.73
best_ask = best_bid + tick

# Price ladders
bid_prices = best_bid - tick * np.arange(n_levels)   # high -> low
ask_prices = best_ask + tick * np.arange(n_levels)   # low  -> high

# Sizes with slight depth taper (app-like)
base_bids = np.random.lognormal(mean=-0.1, sigma=0.55, size=n_levels)
base_asks = np.random.lognormal(mean=-0.1, sigma=0.55, size=n_levels)
depth_shape = np.linspace(1.15, 0.75, n_levels)

bid_sizes = base_bids * depth_shape
ask_sizes = base_asks * depth_shape

# Draw ladder
plot_order_book_ladder(
    bid_prices, bid_sizes, ask_prices, ask_sizes,
    title="ETH-USDC", n_levels=40
)

# Draw depth
plot_depth_chart(
    bid_prices, bid_sizes, ask_prices, ask_sizes,
    title="Depth", n_levels=60
)