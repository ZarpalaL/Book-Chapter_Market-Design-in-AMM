import matplotlib
matplotlib.use("TkAgg")  # Use an interactive backend for displaying plots

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import simpy
from scipy.interpolate import interp1d

class LiquidityPool:
    def __init__(self, q_reserve, y_reserve, K, fee_rate):
        self.q_reserve = q_reserve  # Risky asset reserve
        self.y_reserve = y_reserve  # Stablecoin reserve
        self.K = K  # Liquidity constant
        self.fee_rate = fee_rate  # Trading fee rate

    def invariant_function(self, q, y):
        """Invariant function F_i(q, y) = K."""
        return q * y

    def price_function(self, q, y):
        """Pricing function P_i(q, y)."""
        return y / q

    def trade(self, delta_y):
        """Simulate a trade and update reserves."""
        new_y_reserve = self.y_reserve + delta_y
        delta_q = self.q_reserve - (self.K / new_y_reserve)
        self.q_reserve -= delta_q
        self.y_reserve = new_y_reserve

        # Apply trading fee
        fee = abs(delta_y) * self.fee_rate
        return delta_q, fee

    def calculate_net_return(self, lp, delta_y, theta, fee_function):
        """Calculate the net return \pi_{k,i}(s,z) for an LP."""
        relative_return = lp.calculate_relative_return()
        fees = fee_function(delta_y, theta)
        return relative_return + fees

class Filler:
    def __init__(self, delta, theta):
        self.delta = delta  # Trading budget
        self.theta = theta  # Routing weight

    def route_order(self, pool_a, pool_b):
        """Route the order across the two pools."""
        delta_y_a = self.theta * self.delta
        delta_y_b = (1 - self.theta) * self.delta

        delta_q_a, fee_a = pool_a.trade(delta_y_a)
        delta_q_b, fee_b = pool_b.trade(delta_y_b)

        return {
            "Pool A": {"delta_q": delta_q_a, "fee": fee_a},
            "Pool B": {"delta_q": delta_q_b, "fee": fee_b}
        }

class LiquidityProvider:
    def __init__(self, omega, initial_value):
        self.omega = omega  # Pro-rata contribution (constant)
        self.initial_value = initial_value  # Initial value of the LP's position
        self.current_value = initial_value  # Current value of the LP's position

    def update_value(self, pool_price, pool_reserves):
        """Update the value of the LP's position based on pool price and reserves."""
        y_reserve, q_reserve = pool_reserves
        self.current_value = self.omega * (y_reserve + pool_price * q_reserve)

    def calculate_relative_return(self):
        """Calculate the relative inventory return R_{k,i}."""
        return (self.current_value - self.initial_value) / self.initial_value

# Example fee function
def fee_function(delta_y, theta):
    """Calculate fees \Phi_i(\Delta_y^i,\theta)."""
    return abs(delta_y) * theta * 0.003  # Example fee calculation

# Simulation framework
def main():
    # One Uniswap v2 no-fee pool: USDC (x) / ETH (y)
    x = 50_000.0   # USDC reserve
    y = 100_000.0  # ETH reserve
    k = x * y

    # Pre-trade price of ETH (in USDC)
    p_eth_pre = x / y

    # Trade: deposit Delta_y (ETH), receive Delta_x (USDC)
    delta_y = 10_000.0
    y_new = y + delta_y
    x_new = k / y_new
    delta_x = x - x_new

    # Post-trade price of ETH (in USDC)
    p_eth_post = x_new / y_new

    print("=== Uniswap v2 Single Pool (No Fee) ===")
    print(f"Pre-trade price of ETH  = {p_eth_pre:.9f} USDC")
    print(f"Post-trade price of ETH = {p_eth_post:.9f} USDC")
    print(f"Price change (%)        = {((p_eth_post - p_eth_pre) / p_eth_pre) * 100:.6f}%")
    print(f"x' = {x_new:.6f}, Delta_x = {delta_x:.6f}")

    # Invariant curve: x = k / y
    y_vals = np.linspace(60_000, 140_000, 800)
    x_vals = k / y_vals

    # Segment between trade states is dashed
    y_start, y_end = sorted([y, y_new])
    mask_left = y_vals < y_start
    mask_mid = (y_vals >= y_start) & (y_vals <= y_end)
    mask_right = y_vals > y_end

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(y_vals[mask_left], x_vals[mask_left], color="steelblue", lw=1.4, label="Invariant curve")
    ax.plot(y_vals[mask_mid], x_vals[mask_mid], color="steelblue", lw=1.4, ls="--")
    ax.plot(y_vals[mask_right], x_vals[mask_right], color="steelblue", lw=1.4)

    # Pre/Post trade points
    ax.scatter([y], [x], s=30, color="green", zorder=5, label="Pre-trade state")
    ax.scatter([y_new], [x_new], s=30, color="red", zorder=3, label="Post-trade state")

    # Tangent line at pre-trade point
    # For x = k/y, slope is dx/dy = -k/y^2 = -x/y = -p_eth_pre
    slope = -x / y

    # Make tangent segment longer and high-contrast
    dy_tan = 14_000
    y_tan = np.array([y - dy_tan, y + dy_tan])
    x_tan = x + slope * (y_tan - y)

    ax.plot(
        y_tan, x_tan,
        color="darkorange",
        lw=1.6,      # thinner
        ls="--",
        zorder=4,
        label="Tangent at pre-trade point"
    )

    
  

    # Invariant label box
    ax.text(
        0.38, 0.96,
        r"$xy = k = 5\times10^9$",
        transform=ax.transAxes,
        va="top",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9)
    )

    

    # Pre-trade box near green dot
    ax.text(
        y - 18500, x - 6000,
        f"Pre-trade price of ETH\np = {p_eth_pre:.6f} USDC",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9)
    )

    # Post-trade box near red dot
    ax.text(
        y_new + 1000, x_new + 1200,
        f"Post-trade price of ETH\n$p' = {p_eth_post:.6f}$ USDC",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9)
    )

    ax.set_title("Constant-Product Invariant and Pool Adjustment in a Uniswap v2 USDC/ETH Pool")
    ax.set_xlabel("ETH reserves (y)")
    ax.set_ylabel("USDC reserves (x)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    plt.tight_layout()
    plt.savefig("pool_example_graph.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    main()

