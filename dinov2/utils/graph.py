import torch


def label_graph(gathered_targets, n_global_crops, n_local_crops, device=None):
    """
    Returns: [N_local * bs, N_global * bs] bool matrix
    """
    local_labels  = gathered_targets.repeat_interleave(n_local_crops).unsqueeze(1)   # [N_local, 1]
    global_labels = gathered_targets.repeat_interleave(n_global_crops).unsqueeze(0)  # [1, N_global]
    G = (local_labels == global_labels).bool()  # [N_local * bs, N_global * bs]

    if device is not None:
        G = G.to(device)
    return G


def semisup_graph(
    labels_graph,
    view_graph,
    gathered_is_supervised,
    n_global_crops,
    n_local_crops,
    device=None
):
    
    batch_size = gathered_is_supervised.shape[0]

    local_mask  = gathered_is_supervised.repeat_interleave(n_local_crops).unsqueeze(1).bool()
    global_mask = gathered_is_supervised.repeat_interleave(n_global_crops).unsqueeze(0).bool()
    mask = local_mask & global_mask  # [N_local * bs, N_global * bs]

    G = labels_graph.bool() & mask
    G[view_graph.bool()] = True

    if device is not None:
        G = G.to(device)
    return G


def nview_graph(batch_size, n_global_crops, n_local_crops, device=None):
    """
    Returns: [N_local * bs, N_global * bs] bool matrix
    """
    num_global = batch_size * n_global_crops
    num_local = batch_size * n_local_crops
    G = torch.zeros((num_local, num_global), dtype=torch.bool)

    for i in range(batch_size):
        global_indices = torch.arange(i * n_global_crops, (i + 1) * n_global_crops)
        local_indices  = torch.arange(i * n_local_crops, (i + 1) * n_local_crops)
        G[local_indices.unsqueeze(1), global_indices] = True

    if device is not None:
        G = G.to(device)
    return G


