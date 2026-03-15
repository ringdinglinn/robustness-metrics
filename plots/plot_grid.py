import os
import matplotlib.pyplot as plt

def plot_metrics(metrics, groups, output_dir, sort_by=None):
    linestyles = ["-", "--", "-.", ":"]
    group_names = sorted(groups.keys())
    n_groups = len(group_names)
    n_cols = min(3, n_groups)
    n_rows = (n_groups + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    axes = [axes] if n_groups == 1 else axes.flatten()
    fig.suptitle(" | ".join(metrics), fontsize=14, fontweight="bold")

    all_subgroups = set()
    for subdict in groups.values():
        all_subgroups.update(subdict.keys())
    all_subgroups = sorted(all_subgroups)
    cmap = plt.get_cmap("tab10")
    color_map = {name: cmap(i % 10) for i, name in enumerate(all_subgroups)}

    handles, labels = [], []

    for i, group_name in enumerate(group_names):
        ax = axes[i]
        subgroups = groups[group_name]
        max_y = 0

        for sub_name, rows in subgroups.items():
            if sort_by:
                rows = sorted(rows, key=lambda r: r.get(sort_by, ""))

            for m_idx, metric in enumerate(metrics):
                valid_rows = [r for r in rows if r.get(metric)]
                if not valid_rows:
                    continue

                x_labels = [os.path.basename(r["topology"]).replace(".yaml", "") for r in valid_rows]
                y_values = [float(r[metric]) for r in valid_rows]
                linestyle = linestyles[m_idx % len(linestyles)]
                legend_key = f"{sub_name} ({metric})"

                line, = ax.plot(
                    range(len(y_values)),
                    y_values,
                    marker="o",
                    color=color_map[sub_name],
                    linestyle=linestyle,
                    label=legend_key
                )
                if legend_key not in labels:
                    handles.append(line)
                    labels.append(legend_key)

                max_y = max(max(y_values), max_y)

        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
        ax.set_title(group_name)
        ax.set_ylabel(" | ".join(metrics))
        ax.set_ylim(bottom=0, top=max_y * 1.15)

    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=min(len(labels), 5))
    plt.tight_layout(rect=[0, 0.05, 1, 1])

    os.makedirs(output_dir, exist_ok=True)
    safe_name = "_vs_".join(m.replace(" ", "_").replace("|", "").replace("/", "_") for m in metrics)
    out_path = os.path.join(output_dir, f"{safe_name}.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")