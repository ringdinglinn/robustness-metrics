import os
import matplotlib.pyplot as plt
import ast
import numpy as np

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
            parsed = [ast.literal_eval(r[metric]) for r in rows]
        except (KeyError, ValueError):
            ax.set_title(f"{group_name}\n(metric unavailable)")
            ax.axis("off")
            continue

        all_keys = sorted(set(k for d in parsed for k in d.keys()))
        n_topos = len(rows)
        n_keys = len(all_keys)
        x = np.arange(n_topos)
        bar_width = 0.8 / n_keys

        for j, key in enumerate(all_keys):
            y = [d.get(key, 0) for d in parsed]
            offset = (j - n_keys / 2 + 0.5) * bar_width
            ax.bar(x + offset, y, width=bar_width, label=str(key))

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
        ax.set_title(group_name)
        ax.set_ylabel(metric)
        ax.legend(fontsize=7)

    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    safe_name = metric.replace(" ", "_").replace("|", "").replace("/", "_")
    out_path = os.path.join(output_dir, f"{safe_name}.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")