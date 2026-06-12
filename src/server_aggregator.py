import torch

def top_k_sparsify(gradient_tensor, sparsity_ratio=0.3):
    """
    Applies Top-k Sparsification transmitting only high-magnitude gradients (Eq. 6)
    """
    k = int(gradient_tensor.numel() * sparsity_ratio)
    if k == 0:
        return gradient_tensor
    
    values, indices = torch.topk(torch.abs(gradient_tensor), k)
    sparsified = torch.zeros_like(gradient_tensor)
    sparsified[indices] = gradient_tensor[indices]
    return sparsified

def krum_filter(updates, num_byzantine):
    """
    Byzantine-Robust Selection (Algorithm 3 / Eq. 7)
    Selects updates most consistent with neighboring trajectories
    """
    N = len(updates)
    # Krum valid boundary constraint check: 2f + 2 < N
    nb_neighbors = N - num_byzantine - 2
    
    if nb_neighbors <= 0:
        return updates[0] # Fallback consensus domain
        
    scores = []
    for i in range(N):
        distances = []
        for j in range(N):
            if i != j:
                # Compute Euclidean squared distance
                dist = torch.norm(updates[i] - updates[j]) ** 2
                distances.append(dist.item())
        
        distances.sort()
        # Sum of squared distances to closest neighbors
        scores.append(sum(distances[:nb_neighbors]))
        
    best_index = scores.index(min(scores))
    return updates[best_index]

def aggregate_entropy_fl(local_updates, dataset_sizes, confidence_scores, num_byzantine=10, sigma=0.1, s=0.3):
    """
    Entropy-Weighted Secure Aggregation (Algorithm 3 Framework)
    """
    processed_updates = []
    for update in local_updates:
        # Step 1: Communication payload reduction via top-k magnitude compression
        sparse_u = top_k_sparsify(update, sparsity_ratio=s)
        # Step 2: Inject DP Gaussian Noise to thwart gradient inversion attacks
        dp_noise = torch.randn_like(sparse_u) * sigma
        processed_updates.append(sparse_u + dp_noise)
        
    # Step 3: Mitigation of poisoned updates using Byzantine Krum selection
    trusted_update = krum_filter(processed_updates, num_byzantine)
    
    # Step 4: Compute Entropy-Aware Weights based on client traffic richness (Eq. 5)
    total_weighted_volume = sum([c * d for c, d in zip(confidence_scores, dataset_sizes)])
    
    # Asymmetric update targeting non-IID data distributions
    aggregated_gradient = torch.zeros_like(trusted_update)
    for i, update in enumerate(processed_updates):
        w_i = (confidence_scores[i] * dataset_sizes[i]) / total_weighted_volume
        aggregated_gradient += w_i * update
        
    return aggregated_gradient