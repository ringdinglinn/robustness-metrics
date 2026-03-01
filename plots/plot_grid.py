import os
import matplotlib.pyplot as plt

def plot_metric(metric, groups, output_dir, sort_by):
    group_names = sorted(groups.keys())
    n_groups = len(group_names)
    n_cols = min(3, n_groups)
    n_rows = (n_groups + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    axes = [axes] if n_groups == 1 else axes.flatten()
    fig.suptitle(metric, fontsize=14, fontweight="bold")

    for i, group_name in enumerate(group_names):
        ax = axes[i]
        rows = groups[group_name]
        if sort_by:
            rows = sorted(rows, key=lambda r: r.get(sort_by, ""))

        x_labels = [os.path.basename(r["topology"]).replace(".yaml", "") for r in rows]
        try:
            y_values = [float(r[metric]) for r in rows]
        except (KeyError, ValueError):
            ax.set_title(f"{group_name}\n(metric unavailable)")
            ax.axis("off")
            continue

        ax.bar(range(len(y_values)), y_values, color="steelblue")
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
        ax.set_title(group_name)
        ax.set_ylabel(metric)

    # Hide unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    safe_name = metric.replace(" ", "_").replace("|", "").replace("/", "_")
    out_path = os.path.join(output_dir, f"{safe_name}.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")