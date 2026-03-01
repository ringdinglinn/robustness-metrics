import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute core control and Cheeger constant per ISD country."
    )
    parser.add_argument(
        "--graph",
        required=True,
        help="Networkx Graph"
    )
    parser.add_argument(
        "--output",
        help="Path to the output CSV file (default: results/core_control.csv)."
    )
    return parser.parse_args()

def compute_border_breadth(total_core_edges, total_core_nodes, all_nodes_in_isd):
    core_nodes_without_isd = total_core_nodes - all_nodes_in_isd
    n_outgoing_edges = sum(
        1
        for n1, n2 in total_core_edges
        if (n1 in core_nodes_without_isd) != (n2 in core_nodes_without_isd)
        and (n1 in all_nodes_in_isd or n2 in all_nodes_in_isd)
    )
    return float(n_outgoing_edges) / float(len(all_nodes_in_isd))

def get_core_subgraph(G):
    total_core_nodes = [node for node, is_core in G.nodes(data="is_core") if is_core]
    return G.subgraph(total_core_nodes)

def get_nodes_in_isd(G, isd_n):
    return [node for node, node_isd in G.nodes(data="isd_n") if node_isd == isd_n]

def compute(G):
    total_core = get_core_subgraph(G)
    isds = set([isd for _, isd in G.nodes(data="isd_n")])
    print(f"SCION Core: {len(total_core.nodes)} nodes")
    results = {}

    for isd in isds:
        border_breadth = compute_border_breadth(total_core.edges, set(total_core.nodes), set(get_nodes_in_isd(G, isd)))
        results[isd] = border_breadth

    return { "border_breadth" : results }

def save_results(results, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("cc,out_edges,nodes_in_isd,core_control,isd_ratio,cheeger,cut_ratio\n")
        for cc, (out_edges, nodes_in_isd, core_control, isd_ratio, cheeger, cut_ratio) in results.items():
            f.write(f"{cc},{out_edges},{nodes_in_isd},{core_control},{isd_ratio},{cheeger},{cut_ratio}\n")
    print(f"Results saved to {output_path}")

def main():
    args = parse_args()
    results = compute(args.graph)
    save_results(results, args.output)

if __name__ == "__main__":
    main()