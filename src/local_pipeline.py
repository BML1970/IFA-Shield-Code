import numpy as np
import math

class PoissonEMADetector:
    def __init__(self, window_size=30, alpha=0.2, k_multiplier=3.0):
        self.W = window_size          # Sliding window size for rate estimation
        self.alpha = alpha            # EMA smoothing factor
        self.k = k_multiplier         # Confidence metric multiplier (3-sigma rule)
        self.traffic_history = []     # Slided packet count window
        self.mu = 0.0                 # Stabilized traffic baseline

    def calculate_prefix_entropy(self, prefix_counts):
        """
        Computes Shannon Entropy of incoming Interest hierarchical name prefixes (Eq. 1)
        """
        total_interests = sum(prefix_counts.values())
        if total_interests == 0:
            return 0.0
        
        entropy = 0.0
        for count in prefix_counts.values():
            p_i = count / total_interests
            entropy -= p_i * math.log2(p_i)
        return entropy

    def process_epoch(self, current_packet_count):
        """
        Executes Poisson-EMA Dynamic Thresholding (Algorithms 2 & 5)
        """
        self.traffic_history.append(current_packet_count)
        if len(self.traffic_history) > self.W:
            self.traffic_history.pop(0)
            
        # Step 1: Maximum Likelihood Estimation for Poisson Rate parameter (Eq. 2)
        lambda_t = np.mean(self.traffic_history)
        
        # Step 2: Exponential Smoothing Baseline (Eq. 3)
        if self.mu == 0.0:
            self.mu = float(current_packet_count)
        else:
            self.mu = (self.alpha * current_packet_count) + ((1.0 - self.alpha) * self.mu)
            
        # Step 3: Compute Dynamic Threshold incorporating Poisson variance (Eq. 4)
        # In a Poisson process, variance equals the mean, hence standard deviation is sqrt(mu)
        tau_t = lambda_t + (self.k * math.sqrt(self.mu))
        
        # Step 4: Anomaly Scoring and Classification Bounds
        if current_packet_count > tau_t:
            # Local anomaly score normalized by intensity deviation
            p_a_local = min(1.0, (current_packet_count - tau_t) / current_packet_count)
            return p_a_local, True  # Action triggered: Flag Suspicious
        else:
            return 0.0, False       # Classify Benign / Forward Interest