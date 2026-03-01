import networkx as nx
import metrics.network_partition as network_partition

def calculate_metrics(G, graph_name):
    metrics = {}
    metrics['transitivity']         = nx.transitivity(G)
    print(f"{graph_name}, transitivity: {metrics['transitivity']}")
    metrics['average_clustering']   = nx.average_clustering(G)
    print(f"{graph_name}, average_clustering: {metrics['average_clustering']}")
    metrics['cheeger constant'], _  = network_partition.compute(G)
    print(f"{graph_name}, cheeger: {metrics['cheeger constant']}")

    return metrics

def compute(G):
    metrics = calculate_metrics(G)
    return metrics
