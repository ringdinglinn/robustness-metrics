import math
import json
import networkx as nx
import torch
import numpy as np
import time
import matplotlib.pyplot as plt

# --- Utilities ----------------------------------------------------------------

MIN_PART_SIZE = 1

def is_balanced(a, b, is_a, r, n):
    m = 0.05

    if (is_a):
        a -= 1
        b += 1
    else:
        a += 1
        b -= 1
    s = min(a, b)

    max_m = round(n * m)
    s_r = round(min(n * r, n * (1 - r)))

    balance_ok = (abs(s_r - s) <= max_m)
    non_empty_ok = (a > 0) & (b > 0)

    return balance_ok & non_empty_ok

def update_gains(G, idx_to_node, node_to_idx, assignment, gains, vertex):
    gains[vertex] = -np.inf
    node = idx_to_node[vertex]
    cut_edges = 0
    for neighbor in G.neighbors(node):
        j = node_to_idx[neighbor]
        # Before move: check if edge was cut
        # After move: assignment[vertex] flips
        if assignment[vertex] == assignment[j]:
            # Same partition BEFORE move → edge NOT cut
            # After move → edge WILL BE cut
            gains[j] += 2  # Moving vertex away increases neighbor's gain
            cut_edges += 1  # One more cut edge
        else:
            # Different partition BEFORE move → edge IS cut
            # After move → edge will NOT be cut
            gains[j] -= 2  # Moving vertex closer decreases neighbor's gain
            cut_edges -= 1  # One fewer cut edge
    return cut_edges

def intialize_gains(G, idx_to_node, node_to_idx, assignment):
    n = assignment.shape[0]
    gains = np.zeros(n)
    n_cut_edges = 0
    for i in range(n):
        node = idx_to_node[i]
        for neighbor in G.neighbors(node):
            j = node_to_idx[neighbor]
            if assignment[j] != assignment[i]:
                gains[i] += 1
                n_cut_edges += 1
            else:
                gains[i] -= 1

    n_cut_edges //= 2
    order = np.argsort(-gains)
    return gains, order, n_cut_edges


# --- Algorithm ---------------------------------------------------------------

def initial_partition(n, r):
    perm = torch.randperm(n)
    r = min(1 - r, r)
    k = max(1, round(n * r))
    A_idx = perm[:k]
    assignment = np.ones(n)
    assignment[A_idx] = -1
    return assignment, k, n - k

def calulate_cheeger(n_cut, size_a, size_b):
    return n_cut / min(size_a, size_b)

def partition_pass(G, r):
    idx_to_node = {i:node for i, node in enumerate(list(G.nodes()))}
    node_to_idx = {node:i for i, node in enumerate(list(G.nodes()))}
    n = len(G.nodes())
    if n == 0:
        return None

    assignment, size_a, size_b = initial_partition(n, r)

    moveable = np.ones(n, dtype=bool)

    gains, order, n_cut_edges = intialize_gains(G, idx_to_node, node_to_idx, assignment) 

    min_cut_edges = np.inf
    best_assignemnt = assignment.copy() 

    while (moveable).any().item():
        idx = 0
        vertex = order[idx]

        while idx < len(gains) :
            vertex = order[idx]
            if ((not is_balanced(size_a, size_b, assignment[vertex]==-1, r, n) or not moveable[vertex])):
                idx += 1
            else:
                break

        if idx == len(gains):
            break

        # update stuff

        if assignment[vertex] == -1:
            size_a -= 1
            size_b += 1
        else:
            size_a += 1
            size_b -= 1

        delta_edges = update_gains(G, idx_to_node, node_to_idx, assignment, gains, vertex)
        n_cut_edges += delta_edges
        assignment[vertex] *= -1

        moveable[vertex] = False

        order = np.argsort(-gains)

        if (min_cut_edges > n_cut_edges):
            min_cut_edges = n_cut_edges
            best_assignemnt = assignment.copy()

    return min_cut_edges, np.sum(best_assignemnt==-1), np.sum(best_assignemnt==1)

# --- Top-level helpers -------------------------------------------------------

def cheeger(c, a, b):
    return c / min(a, b)

def run_passes(G, r, n_passes):
    min_cheeger = math.inf
    updates = 0
    min_partition = None

    for i in range(n_passes):
        res = partition_pass(G, r)
        if res is None:
            print(f"pass {i}: no improving moves (empty or trivial partition).")
            continue
        c, a, b = res

        current = cheeger(c, a, b)
        if current < min_cheeger:
            min_cheeger = current
            updates += 1
            min_partition = (c, a, b)

        print(f"pass: {i}, updates: {updates}, cur_cheeger: {current:.6f}, a = {a}, b = {b}")

    return min_partition

# --- JSON encoder for torch types -------------------------------------------

class TorchJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if torch.is_tensor(obj):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)

# --- main --------------------------------------------------------------------

def compute_r(G, r_s, passes):
    results_r = {}
    for r in r_s:
        start = time.time()
        res = run_passes(G, r, passes)
        elapsed = time.time() - start
        if res is None:
            results_r[str(r)] = None
        else:
            c, a, b = res
            results_r[str(r)] = {"cheeger": cheeger(c, a, b), "c": c, "a": a, "b": b}
        print(f"r={r}: {elapsed:.2f}s")

    return min([r["cheeger"] for r in results_r.values()])

def compute(G):
    r_s = [0.05, 0.15, 0.25, 0.35, 0.45]
    passes = 10
    return compute_r(G, r_s, passes)
