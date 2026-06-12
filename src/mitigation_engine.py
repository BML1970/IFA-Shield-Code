class ThreeTierMitigationEngine:
    def __init__(self):
        # Operational Confidence Barrier Constraints
        self.T_alert = 0.5
        self.T_mitigate = 0.7
        self.T_critical = 0.9
        
    def enforce_defense(self, prefix, p_a, pit_occupancy):
        """
        Executes an escalating graduated response strategy (Algorithm 4)
        """
        actions = []
        
        if p_a >= self.T_critical:
            # Tier 3: Cryptographic Blacklisting (Isolation phase)
            actions.append({
                "tier": 3,
                "action": "CRYPTOGRAPHIC_BLACKLIST",
                "prefix": prefix,
                "duration": "30s_exponential_backoff",
                "log": "DISTRIBUTED_LEDGER_AUDIT"
            })
            
        elif p_a >= self.T_mitigate:
            # Tier 2: Logical PIT Partitioning
            # Reserve 30% capacity exclusively for verified legitimate traffic vectors
            actions.append({
                "tier": 2,
                "action": "PARTITION_PIT",
                "prefix": prefix,
                "quarantine_allocation": "isolate_suspicious",
                "guaranteed_benign_capacity": "30%"
            })
            
        elif p_a >= self.T_alert:
            # Tier 1: Dynamic Token Bucket Rate Limiting
            actions.append({
                "tier": 1,
                "action": "RATE_LIMIT_TOKEN_BUCKET",
                "prefix": prefix,
                "refill_rate_adaptation": f"dynamic_scaled_by_{pit_occupancy}"
            })
        else:
            actions.append({"tier": 0, "action": "FORWARD_INTEREST_NORMAL"})
            
        # Closed-loop feedback mechanism checking if mitigation failed to stabilize PIT
        if pit_occupancy > 0.85:
            actions.append({
                "escalation": True,
                "reason": "PIT occupancy threshold breached post-mitigation (>85%)",
                "instruction": "FORCE_STEP_UP_TIER"
            })
            
        return actions