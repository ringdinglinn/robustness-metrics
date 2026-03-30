"""
cheeger_torch.py

PyTorch-based conversion of your partitioning / Cheeger search script.
Uses sparse COO-style tensors (row_idx, col_idx, data) stored as 1-D torch tensors
to avoid densifying large adjacency matrices.

Run:
    python cheeger_torch.py <edgelist_file>

Outputs a JSON file at ../results/cheeger_2.json (create directory if needed).
"""
import math
import json
import networkx as nx
import torch
import numpy as np
import time

# --- Utilities ----------------------------------------------------------------

MIN_PART_SIZE = 1

def update_balanced(balanced, assignment, r):
    """
    Updates the balanced tensor in-place.
    - balanced: torch.BoolTensor of shape (n,)
    - assignment: torch.IntTensor of shape (n,) with values ±1
    - r: float, target fraction
    """
    m = 0.05

    n = assignment.numel()
    num_neg = (assignment == -1).sum().item()
    num_pos = n - num_neg

    a = num_neg + assignment
    b = num_pos - assignment
    s = torch.minimum(a, b)

    max_m = round(n * m)
    s_r = round(min(n * r, n * (1 - r)))

    # in-place update
    balance_ok = (torch.abs(s_r - s) <= max_m)
    non_empty_ok = (a > 0) & (b > 0)

    # in-place update
    balanced.copy_(balance_ok & non_empty_ok)

# --- Sparse helpers -----------------------------------------------------------

def compute_cut_data_from_adj(adj_row, adj_col, adj_data, assignment):
    """
    Given adjacency in COO (adj_row, adj_col, adj_data) and assignment (tensor of ±1),
    compute cut_matrix = adj @ diag(assignment) in COO-value form.
    For each nonzero (i,j) of adj, cut_value = adj_value * assignment[j].
    Returns cut_row, cut_col, cut_data (same indices as adjacency with new values).
    (We simply reuse adj_row/adj_col and modify data.)
    """
    # assignment is 1-D tensor (n,), and adj_col indexes into it
    cut_data = adj_data * assignment[adj_row] * assignment[adj_col].to(adj_data.dtype)
    return adj_row, adj_col, cut_data

def row_sum_from_coo(row_idx, values, n_rows, dtype=torch.float32):
    """
    Given COO (row_idx, values), compute row-wise sum vector of length n_rows.
    Uses scatter_add.
    """
    row_sums = torch.zeros(n_rows, dtype=values.dtype)
    row_sums = row_sums.scatter_add(0, row_idx, values)
    return row_sums

def create_cut(cut_data, assignment):
    n_cuts_raw = int((cut_data == -1).sum().item())
    n_cuts = n_cuts_raw // 2

    a, b = int((assignment == -1).sum().item()), int((assignment == 1).sum().item())
    return (n_cuts, a, b)

# --- Algorithm ---------------------------------------------------------------

def initial_partition(n, r):
    perm = torch.randperm(n)
    r = min(1 - r, r)
    k = max(1, round(n * r))
    A_idx = perm[:k]
    assignment = torch.ones(n, dtype=torch.int32)
    assignment[A_idx] = -1
    return assignment

def partition_pass(G, r):
    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return None

    # Mapping from node label -> contiguous index [0..n-1]
    # Build adjacency as COO via scipy then to torch
    adj_sp = nx.to_scipy_sparse_array(G).tocoo()
    # Sanity: if adjacency has shape mismatch, handle it
    assert adj_sp.shape[0] == n and adj_sp.shape[1] == n, "Adjacency shape mismatch with node list"

    adj_row = torch.tensor(adj_sp.row, dtype=torch.long)
    adj_col = torch.tensor(adj_sp.col, dtype=torch.long)
    adj_data = torch.tensor(adj_sp.data, dtype=torch.float32)

    # initial random partition: choose k nodes for A (assignment -1), rest 1
    assignment = initial_partition(n, r)

    moveable = torch.ones(n, dtype=torch.bool)

    # Compute cut_matrix = adj @ diag(assignment) in COO form
    cut_row, cut_col, cut_data = compute_cut_data_from_adj(adj_row, adj_col, adj_data, assignment)

    # balanced per vertex
    balanced = torch.ones(n, dtype=torch.bool)
    update_balanced(balanced, assignment, r)

    cuts = []
    
    cuts.append(create_cut(cut_data, assignment))

    while (moveable & balanced).any().item():
        row_sums = row_sum_from_coo(cut_row, cut_data, n)
        gains = - row_sums

        # Find candidate indices where moveable & balanced
        candidates = torch.where(moveable & balanced)[0]
        if candidates.numel() == 0:
            break

        candidate_vals = gains[candidates]
        # choose the candidate with maximum gain (ties broken arbitrarily)
        max_idx = torch.argmax(candidate_vals)
        max_vertex = int(candidates[max_idx].item())

        # flip assignment for that vertex
        assignment[max_vertex] *= -1

        # Update cut_data: because cut_data = adj_value * assignment[col]
        # flipping assignment[v] toggles sign of all entries with col == v
        affected = (cut_col == max_vertex) | (cut_row == max_vertex)
        if affected.any().item():
            cut_data[affected] *= -1        

        # Update balanced after flip
        update_balanced(balanced, assignment, r)

        cuts.append(create_cut(cut_data, assignment))

        # mark vertex as non-moveable
        moveable[max_vertex] = False

    return min(cuts, key=lambda x: x[0]) if cuts else None

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

def compute(G):
    r_s = [0.05, 0.15, 0.25, 0.35, 0.45]
    results_r = {}
    for r in r_s:
        start = time.time()
        res = run_passes(G, r, 10)
        elapsed = time.time() - start
        if res is None:
            results_r[str(r)] = None
        else:
            c, a, b = res
            results_r[str(r)] = {"cheeger": cheeger(c, a, b), "c": c, "a": a, "b": b}
        print(f"r={r}: {elapsed:.2f}s")

    return min([r["cheeger"] for r in results_r.values()])