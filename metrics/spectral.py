import networkx as nx
import numpy as np
from scipy import sparse

def spectral_gap(e):
    return e[0] - e[1]

def spectral_radius(e):
    return e[0]

def compute(G):
    metrics = {}
    n = len(G.nodes())
    k = min(n-1, 3)
    A = sparse.coo_matrix(nx.adjacency_matrix(G))
    e_vals, e_vecs = sparse.linalg.eigsh(A, k=k, which='LA', tol=1e-10)
    pairs = list(zip(e_vals, e_vecs.T))
    pairs.sort(key=lambda x: x[0], reverse=True)
    e_vals = np.array([p[0] for p in pairs])
    e_vecs = np.column_stack([p[1] for p in pairs])
    print(e_vals)
    metrics["spectral_gap"] = spectral_gap(e_vals)
    metrics["spectral_radius"] = spectral_radius(e_vals)

    L = sparse.coo_matrix(nx.laplacian_matrix(G))
    e_, _ = sparse.linalg.eigsh(L, k=k, which='SA', tol=1e-10)
    e_ = np.sort(e_)

    metrics["algebraic_connectivity"] = e_[1]

    return metrics