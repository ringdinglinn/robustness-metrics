import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import networkx as nx
import numpy as np
import colorsys

def get_node_colors(G):
    isds = sorted(set(data["isd_n"] for _, data in G.nodes(data=True)))
    
    # Spread hues evenly around the color wheel
    hues = [i / len(isds) for i in range(len(isds))]
    isd_to_hue = {isd: hue for isd, hue in zip(isds, hues)}

    colors = []
    for _, data in G.nodes(data=True):
        hue = isd_to_hue[data["isd_n"]]
        if data.get("is_core"):
            # Core: more saturated, darker
            r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 0.6)
        else:
            # Non-core: lighter, less saturated
            r, g, b = colorsys.hsv_to_rgb(hue, 0.2, 0.95)
        colors.append((r, g, b))
    return colors

def plot_graphs(groups, graphs, output_dir, sort_by=None):
    group_names = sorted(groups.keys())
    n_rows = len(group_names)
    n_cols = max(len(rows) for rows in groups.values())

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))

    if n_rows == 1:
        axes = [axes]
    if n_cols == 1:
        axes = [[ax] for ax in axes]

    for i, group_name in enumerate(group_names):
        rows = groups[group_name]
        if sort_by:
            rows = sorted(rows, key=lambda r: r.get(sort_by, ""))

        for j, row in enumerate(rows):
            ax = axes[i][j]
            name = os.path.basename(row["topology"]).replace(".yaml", "")
            G = graphs[name]

            pos = nx.spring_layout(G, seed=42)
            node_colors = get_node_colors(G)
            labels = {node: data["label"] for node, data in G.nodes(data=True)}

            nx.draw(G, pos, ax=ax, labels=labels, node_color=node_colors,
                    node_size=300, font_size=7, edge_color="gray")
            ax.set_title(f"{group_name}\n{name}", fontsize=8)

        for j in range(len(rows), n_cols):
            axes[i][j].axis("off")

    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "graphs.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")