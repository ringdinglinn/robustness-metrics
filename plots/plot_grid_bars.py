import os
import matplotlib.pyplot as plt
import ast
import numpy as np

def plot_metric_grid(metric, groups, output_dir, sort_by):
    col_names = sorted(groups.keys())
    row_names = sorted(set(r for col in groups.values() for r in col.keys()))
    n_cols = len(col_names)
    n_rows = len(row_names)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows), squeeze=False)
    fig.suptitle(metric, fontsize=14, fontweight="bold")

    for col_idx, col_name in enumerate(col_names):
        for row_idx, row_name in enumerate(row_names):
            ax = axes[row_idx][col_idx]
            rows = groups[col_name].get(row_name, [])

            if not rows:
                ax.axis("off")
                continue

            if sort_by:
                rows = sorted(rows, key=lambda r: r.get(sort_by, ""))

            x_labels = [os.path.basename(r["topology"]).replace(".yaml", "") for r in rows]

            try:
                parsed = [ast.literal_eval(r[metric]) for r in rows]
            except (KeyError, ValueError):
                ax.set_title(f"{col_name} / {row_name}\n(metric unavailable)")
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
            ax.set_title(f"{col_name} / {row_name}")
            ax.set_ylabel(metric)
            ax.legend(fontsize=7)

    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    safe_name = metric.replace(" ", "_").replace("|", "").replace("/", "_")
    out_path = os.path.join(output_dir, f"{safe_name}.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")