import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── shared style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 200,
})

COLORS = {
    "Text-only":  "#2c7bb6",
    "Adaptive":   "#1a9850",
    "Image-only": "#f46d43",
    "Hybrid":     "#756bb1",
}

STRATEGIES = ["Text-only", "Adaptive", "Image-only", "Hybrid"]

# ── Chart 1: grouped bar – strategy performance across 7 metrics ──────────────
metrics = ["Text\nsimilarity", "Heading\nstructure", "List\nstructure",
           "Table\nstructure", "Code\nblocks", "Paragraph\nstructure",
           "Word\noverlap"]

data = {
    "Text-only":  [0.860, 0.565, 0.859, 0.922, 0.889, 0.726, 0.761],
    "Adaptive":   [0.838, 0.542, 0.868, 0.956, 0.752, 0.636, 0.794],
    "Image-only": [0.827, 0.429, 0.914, 0.944, 0.250, 0.156, 0.811],
    "Hybrid":     [0.818, 0.348, 0.891, 0.944, 0.736, 0.597, 0.795],
}

n_metrics = len(metrics)
n_strat = len(STRATEGIES)
x = np.arange(n_metrics)
bar_w = 0.19
offsets = np.linspace(-(n_strat - 1) / 2, (n_strat - 1) / 2, n_strat) * bar_w

fig, ax = plt.subplots(figsize=(12, 5.5))

for i, strat in enumerate(STRATEGIES):
    bars = ax.bar(x + offsets[i], data[strat], bar_w,
                  label=strat, color=COLORS[strat], edgecolor="white", linewidth=0.5)

ax.set_xticks(x)
ax.set_xticklabels(metrics, ha="center")
ax.set_ylim(0, 1.08)
ax.set_ylabel("Mean score (0–1)")
ax.set_title("Strategy performance across all seven metrics (90 pages)")
ax.legend(loc="upper right", framealpha=0.9)
ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig("performance.png", bbox_inches="tight")
plt.close(fig)
print("Saved performance.png")

# ── Chart 2: processing time – vertical bars ─────────────────────────────────
times_ms = [197.3, 20790.1, 64696.3, 68009.5]
multipliers = ["1×", "105×", "328×", "345×"]
colors_v = [COLORS[s] for s in STRATEGIES]

# two-line x-tick labels: strategy name + multiplier
tick_labels = [f"{s}\n({m})" for s, m in zip(STRATEGIES, multipliers)]

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(tick_labels, times_ms, color=colors_v,
              edgecolor="white", linewidth=0.5, width=0.55)

ax.set_yscale("log")
ax.set_ylim(bottom=80, top=max(times_ms) * 3)
ax.set_ylabel("Mean processing time per page (ms, log scale)")
ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# ms value inside each bar at geometric mid-height
y_bottom = 80
for bar, val in zip(bars, times_ms):
    mid = (y_bottom * val) ** 0.5
    color = "white" if val > 1000 else "black"
    ax.text(bar.get_x() + bar.get_width() / 2, mid,
            f"{val:,.0f} ms",
            ha="center", va="center", fontsize=9.5,
            fontweight="bold", color=color)

fig.tight_layout()
fig.savefig("efficiency.png", bbox_inches="tight")
plt.close(fig)
print("Saved efficiency.png")
